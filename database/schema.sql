-- ============================================================
--  Система учёта ресурсов  ООО ТК Новочебоксарский  v2
--  Полная схема БД (целые числа для количеств)
-- ============================================================

CREATE DATABASE IF NOT EXISTS greenhouse_diploma
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE greenhouse_diploma;

-- ── Пользователи ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    username   VARCHAR(50)  NOT NULL UNIQUE,
    password   VARCHAR(255) NOT NULL,
    full_name  VARCHAR(100) NOT NULL,
    role       ENUM('admin','storekeeper') NOT NULL DEFAULT 'storekeeper',
    is_active  TINYINT(1) NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ── Категории ─────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS categories (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(100) NOT NULL UNIQUE,
    description TEXT
) ENGINE=InnoDB;

-- ── Единицы измерения ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS units (
    id   INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(20) NOT NULL UNIQUE
) ENGINE=InnoDB;

-- ── Материалы (quantity и min_quantity — INT) ─────────────────
CREATE TABLE IF NOT EXISTS materials (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    name         VARCHAR(150) NOT NULL,
    category_id  INT NOT NULL,
    unit_id      INT NOT NULL,
    quantity     INT NOT NULL DEFAULT 0,
    min_quantity INT NOT NULL DEFAULT 0,
    price        DECIMAL(12,2) NOT NULL DEFAULT 0,
    description  TEXT,
    created_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id),
    FOREIGN KEY (unit_id)     REFERENCES units(id)
) ENGINE=InnoDB;

-- ── Поступления ───────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS receipts (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    material_id     INT NOT NULL,
    quantity        INT NOT NULL,
    price           DECIMAL(12,2) NOT NULL DEFAULT 0,
    supplier        VARCHAR(150),
    document_number VARCHAR(50),
    note            TEXT,
    user_id         INT NOT NULL,
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (material_id) REFERENCES materials(id),
    FOREIGN KEY (user_id)     REFERENCES users(id)
) ENGINE=InnoDB;

-- ── Списания ──────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS writeoffs (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    material_id     INT NOT NULL,
    quantity        INT NOT NULL,
    reason          VARCHAR(255),
    document_number VARCHAR(50),
    note            TEXT,
    user_id         INT NOT NULL,
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (material_id) REFERENCES materials(id),
    FOREIGN KEY (user_id)     REFERENCES users(id)
) ENGINE=InnoDB;

-- ── Журнал событий ────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS event_logs (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    user_id    INT,
    action     VARCHAR(100) NOT NULL,
    details    TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- ── ALTER: конвертировать существующие DECIMAL → INT ──────────
-- (Выполни если таблицы уже созданы с DECIMAL)
-- ALTER TABLE materials  MODIFY quantity     INT NOT NULL DEFAULT 0;
-- ALTER TABLE materials  MODIFY min_quantity INT NOT NULL DEFAULT 0;
-- ALTER TABLE receipts   MODIFY quantity     INT NOT NULL;
-- ALTER TABLE writeoffs  MODIFY quantity     INT NOT NULL;

-- ── Начальные данные ──────────────────────────────────────────
INSERT IGNORE INTO users (username, password, full_name, role) VALUES
('admin',       SHA2('admin123',256), 'Администратор системы',   'admin'),
('storekeeper', SHA2('store123', 256), 'Иванов Иван Иванович',   'storekeeper');

INSERT IGNORE INTO categories (name) VALUES
('Удобрения'),('Средства защиты растений'),('Субстраты и грунты'),
('Инструменты'),('Упаковочные материалы'),('Прочее');

INSERT IGNORE INTO units (name) VALUES
('шт'),('кг'),('л'),('пач'),('м'),('м²'),('т'),('мл');

INSERT IGNORE INTO materials (name,category_id,unit_id,quantity,min_quantity,price) VALUES
('Нитрат аммония',        1,2, 250, 50, 45.00),
('Калий хлористый',       1,2, 180, 30, 38.00),
('Фунгицид Топаз',        2,3,   3,  5,320.00),
('Инсектицид Актара',     2,1,  40, 10,180.00),
('Кокосовый субстрат',    3,2, 500,100, 25.00),
('Перчатки рабочие',      4,1,   8, 20, 15.00),
('Пакеты полиэтиленовые', 5,4,  12,  5, 55.00);
