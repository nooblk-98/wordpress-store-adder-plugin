<?php
/**
 * Plugin Name: Store Locator rest API 
 * Description: A custom plugin to add a REST API endpoint for Store Locator.
 * Version: 1.0
 * Author: lahiru@3cs.solutions
 */

// Include the class file for the custom REST API endpoint.
require_once plugin_dir_path(__FILE__) . 'includes/class-store-locator-api.php';

// Initialize the custom REST API endpoint.
add_action('rest_api_init', array('Store_Locator_API', 'register_routes'));
