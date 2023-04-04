
vk_user = """CREATE TABLE IF NOT EXISTS vk_user (
                        -- id SERIAL PRIMARY KEY,
                       vk_id INTEGER PRIMARY KEY,
                       first_name VARCHAR(40) NOT NULL,
                       last_name VARCHAR(40),
                       );"""

favorites = """CREATE TABLE IF NOT EXISTS favorites ( 
                               vk_id INTEGER NOT NULL,
                               fav_id INTEGER NOT NULL,
                               CONSTRAINT favorites_pk PRIMARY KEY (vk_id, fav_id)
                               );"""


black_list = """CREATE TABLE IF NOT EXISTS black_list (
                                    vk_id INTEGER NOT NULL,
                                    blk_id INTEGER NOT NULL,
                                    CONSTRAINT black_list_pk PRIMARY KEY (vk_id, blk_id)
                                    );"""


last_search = """CREATE TABLE IF NOT EXISTS last_search (
                                  vk_id INTEGER NOT NULL,
                                  lst_id INTEGER NOT NULL,
                                  srch_number INTEGER,
                                  CONSTRAINT last_search_pk PRIMARY KEY (vk_id, lst_id)
                                  );"""

settings = """CREATE TABLE IF NOT EXISTS settings (
                    vk_id INTEGER NOT NULL UNIQUE,
                    age_from INTEGER,
                    age_to INTEGER,
                    );"""

CREATE_TABLES = vk_user + favorites + black_list + \
                last_search + settings

drop_vk_user = """DROP TABLE vk_user;"""
drop_favorites = """DROP TABLE favorites;"""
drop_black_list = """DROP TABLE black_list;"""
drop_last_search = """DROP TABLE last_search;"""
drop_settings = """DROP TABLE settings;"""

DROP_TABLES = drop_last_search + drop_favorites + drop_black_list + \
              drop_settings + drop_vk_user


