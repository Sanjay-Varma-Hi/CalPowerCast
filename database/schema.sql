-- Database schema for CalPowerCast
-- Create power_consumption table

-- Create the database (run this separately if needed)
-- CREATE DATABASE powercast;

-- Create the power_consumption table
CREATE TABLE IF NOT EXISTS power_consumption (
    id SERIAL PRIMARY KEY,
    county TEXT NOT NULL,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL CHECK (month >= 1 AND month <= 12),
    sector TEXT NOT NULL,
    consumption_gwh FLOAT NOT NULL
);

-- Create indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_county ON power_consumption(county);
CREATE INDEX IF NOT EXISTS idx_year_month ON power_consumption(year, month);
CREATE INDEX IF NOT EXISTS idx_sector ON power_consumption(sector);

-- Add a unique constraint to prevent duplicate entries
CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_entry ON power_consumption(county, year, month, sector);

-- Create the normalized_power table for household-normalized consumption
CREATE TABLE IF NOT EXISTS normalized_power (
    id SERIAL PRIMARY KEY,
    county TEXT NOT NULL,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL CHECK (month >= 1 AND month <= 12),
    kwh_per_household FLOAT NOT NULL
);

-- Create indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_norm_county ON normalized_power(county);
CREATE INDEX IF NOT EXISTS idx_norm_year_month ON normalized_power(year, month);
CREATE INDEX IF NOT EXISTS idx_norm_county_year ON normalized_power(county, year);

-- Add a unique constraint to prevent duplicate entries
CREATE UNIQUE INDEX IF NOT EXISTS idx_norm_unique_entry ON normalized_power(county, year, month);
