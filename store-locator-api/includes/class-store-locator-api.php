<?php
class Store_Locator_API {
  
  
    public static function register_routes() {
        register_rest_route('store-locator/v1', '/add-store', array(
            'methods' => 'POST',
            'callback' => array('Store_Locator_API', 'add_new_store'),
            'permission_callback' => function () {
                return current_user_can('edit_posts');
            }
        ));
    }
  
  

    public static function add_new_store(WP_REST_Request $request) {
        $parameters = $request->get_json_params();

        // Validate the parameters
        if (!isset($parameters['name']) || !isset($parameters['address']) || !isset($parameters['city']) || !isset($parameters['country'])) {
            return new WP_Error('missing_parameters', 'Missing required parameters', array('status' => 400));
        }
      
        // Check if a store with the same name already exists
        $existing_posts = get_posts(array(
            'post_type' => 'wpsl_stores',
            'posts_per_page' => -1,
            'title' => $parameters['name'],
            'post_status' => 'publish'
        ));

        if (!empty($existing_posts)) {
            return new WP_REST_Response(array('message' => 'Store already exists', 'store_id' => $existing_posts[0]->ID), 200);
        }


        // Concatenate the address components to form the full address
        $full_address = $parameters['address'] . ', ' . $parameters['city'] . ', ' . (isset($parameters['state']) ? $parameters['state'] . ', ' : '') . $parameters['country'];

        // Use the Google Maps Geocoding API to get the latitude and longitude
        $api_key = get_option('google_maps_api_key');
        $response = wp_remote_get('https://maps.googleapis.com/maps/api/geocode/json?address=' . urlencode($full_address) . '&key=' . $api_key);
        if (is_wp_error($response)) {
            return new WP_Error('geocoding_failed', 'Failed to get coordinates from address', array('status' => 500));
        }

        $data = json_decode(wp_remote_retrieve_body($response), true);
        if (empty($data['results'])) {
            return new WP_Error('geocoding_failed', 'Failed to get coordinates from address', array('status' => 500));
        }

        $latitude = $data['results'][0]['geometry']['location']['lat'];
        $longitude = $data['results'][0]['geometry']['location']['lng'];

        // Create a new post for the store with post_type set to 'wpsl_stores'
        $post_id = wp_insert_post(array(
            'post_title' => $parameters['name'],
            'post_type' => 'wpsl_stores',
            'post_status' => 'publish',
        ));

        if ($post_id) {
            // Update post meta with store details
            update_post_meta($post_id, 'wpsl_address', $parameters['address']);
            update_post_meta($post_id, 'wpsl_city', $parameters['city']);
            update_post_meta($post_id, 'wpsl_state', isset($parameters['state']) ? $parameters['state'] : '');
            update_post_meta($post_id, 'wpsl_country', $parameters['country']);
            update_post_meta($post_id, 'wpsl_lat', $latitude);
            update_post_meta($post_id, 'wpsl_lng', $longitude);

            return new WP_REST_Response(array('message' => 'Store added successfully', 'store_id' => $post_id), 200);
        } else {
            return new WP_Error('store_add_failed', 'Failed to add new store', array('status' => 500));
        }
    }
}
