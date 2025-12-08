-- Migration: Add service_category column to orders table
-- Run this SQL script to update existing database

-- Add service_category column
ALTER TABLE orders 
ADD COLUMN service_category ENUM(
    'cleaner', 'electrician', 'plumber', 'mechanic', 
    'mover', 'technician', 'painter', 'gardener', 'carpenter'
) NOT NULL DEFAULT 'cleaner' AFTER service_name;

-- Update existing orders with default category (you may want to manually update these)
-- This sets all existing orders to 'cleaner' as default
-- You should review and update them based on their service_name

-- Note: After running this migration, you may want to update existing orders
-- based on their service_name using the service_mapper utility

