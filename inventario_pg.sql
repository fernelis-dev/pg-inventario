-- Active: 1709567835577@@127.0.0.1@3306@inventario_pg
-- Active: 1709567835577@@127.0.0.1@3306@inventario_pg@@127.0.0.1@3306
CREATE TABLE productos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    cantidad INT NOT NULL,
    precio DECIMAL(10,2) NOT NULL
);


