-- Creación de tipos ENUM para package_type y content_unit
CREATE TYPE package_type AS ENUM ('sack', 'drum', 'box', 'package');
CREATE TYPE content_unit AS ENUM ('kg', 'liters');
CREATE TYPE movement_type AS ENUM ('entry', 'transfer', 'exit');

-- Creación de la tabla category
CREATE TABLE category (
    category_id INT PRIMARY KEY,
    name_cat VARCHAR(255),
    description_cat TEXT,
    created_at TIMESTAMP
);

-- Creación de la tabla product
CREATE TABLE product (
    product_id INT PRIMARY KEY,
    name_prod VARCHAR(255),
    added_at TIMESTAMP,
    category_id INT,
    FOREIGN KEY (category_id) REFERENCES category(category_id)
);

-- Creación de la tabla presentation
CREATE TABLE presentation (
    presentation_id INT PRIMARY KEY,
    product_id INT,
    package_type package_type,
    content_value FLOAT,
    content_unit content_unit,
    FOREIGN KEY (product_id) REFERENCES product(product_id)
);

-- Creación de la tabla warehouse
CREATE TABLE warehouse (
    ware_id INT PRIMARY KEY,
    name_ware VARCHAR(255),
    description TEXT,
    type VARCHAR(255),
    created_at TIMESTAMP
);

-- Creación de la tabla inventory
CREATE TABLE inventory (
    inventory_id INT PRIMARY KEY,
    product_id INT,
    presentation_id INT,
    ware_id INT,
    quantity INT,
    FOREIGN KEY (product_id) REFERENCES product(product_id),
    FOREIGN KEY (presentation_id) REFERENCES presentation(presentation_id),
    FOREIGN KEY (ware_id) REFERENCES warehouse(ware_id)
);

-- Creación de la tabla user
CREATE TABLE "user" (
    id_user INT PRIMARY KEY,
    name_user VARCHAR(255),
    password_hash VARCHAR(255),
    phone VARCHAR(255),
    email VARCHAR(255)
);

-- Creación de la tabla movement
CREATE TABLE movement (
    move_id INT PRIMARY KEY,
    product_id INT,
    presentation_id INT,
    ware_origin INT,
    ware_destin INT,
    movement_type movement_type,
    quantity FLOAT,
    moved_at TIMESTAMP,
    moved_by INT,
    description TEXT,
    FOREIGN KEY (product_id) REFERENCES product(product_id),
    FOREIGN KEY (presentation_id) REFERENCES presentation(presentation_id),
    FOREIGN KEY (ware_origin) REFERENCES warehouse(ware_id),
    FOREIGN KEY (ware_destin) REFERENCES warehouse(ware_id),
    FOREIGN KEY (moved_by) REFERENCES "user"(id_user)
);

-- Creación de la tabla application_detail
CREATE TABLE application_detail (
    id_detail INT PRIMARY KEY,
    quantity_package INT,
    product_id INT,
    presentation_id INT,
    content_quantity FLOAT,
    application_id INT
    -- La clave foránea para application_id se agregará después de crear la tabla application
);

-- Creación de la tabla application
CREATE TABLE application (
    application_id INT PRIMARY KEY,
    ware_id INT,
    applied_at TIMESTAMP,
    applied_by INT,
    id_detail INT,
    FOREIGN KEY (ware_id) REFERENCES warehouse(ware_id),
    FOREIGN KEY (applied_by) REFERENCES "user"(id_user),
    FOREIGN KEY (id_detail) REFERENCES application_detail(id_detail)
);

-- Se añade la clave foránea que faltaba en application_detail
ALTER TABLE application_detail
ADD CONSTRAINT fk_application
FOREIGN KEY (application_id) REFERENCES application(application_id);

-- Creación de la tabla roles
CREATE TABLE roles (
    id_roles INT PRIMARY KEY,
    name_role VARCHAR(255),
    description_role VARCHAR(255)
);

-- Creación de la tabla user_roles
CREATE TABLE user_roles (
    id_user_roles INT PRIMARY KEY,
    user_id INT,
    role_id INT,
    FOREIGN KEY (user_id) REFERENCES "user"(id_user),
    FOREIGN KEY (role_id) REFERENCES roles(id_roles)
);