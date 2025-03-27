CREATE TABLE users (
    user_id BIGINT PRIMARY KEY,
    username VARCHAR(255) NULL,
    first_name VARCHAR(255) NULL,
    last_name VARCHAR(255) NULL,
    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE sessions (
    session_id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(user_id),
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP NULL,
    completed BOOLEAN DEFAULT FALSE
);

CREATE TABLE route_selections (
    selection_id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES sessions(session_id),
    route_type VARCHAR(50),
    selected BOOLEAN
);

CREATE TABLE location_data (
    location_id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES sessions(session_id),
    departure_city VARCHAR(255),
    lat FLOAT,
    lon FLOAT
);

CREATE TABLE photo_location_selections (
    selection_id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES sessions(session_id),
    photo_location_type VARCHAR(100)
);

CREATE TABLE cuisine_selections (
    selection_id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES sessions(session_id),
    cuisine_type VARCHAR(100)
);

CREATE TABLE route_parameters (
    parameter_id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES sessions(session_id),
    budget FLOAT,
    days INTEGER
);