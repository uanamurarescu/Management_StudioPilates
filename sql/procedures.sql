DROP PROCEDURE IF EXISTS booking_session;
-- PROC_END

CREATE PROCEDURE booking_session(
    IN p_id_client INT,
    IN p_id_user INT,
    IN p_pret INT,
    IN p_durata VARCHAR(10),
    IN p_sessions_json JSON
)
BEGIN
    DECLARE v_abonament_id INT;
    DECLARE v_i INT DEFAULT 0;
    DECLARE v_len INT DEFAULT 0;
    DECLARE v_sesiune_id INT;
    DECLARE v_status_programare VARCHAR(20);

    INSERT INTO Abonamente (Pret, Durata, Activ, fk_idClientA, fk_idUser)
    VALUES (p_pret, p_durata, 'DA', p_id_client, p_id_user);

    SET v_abonament_id = LAST_INSERT_ID();

    SET v_len = JSON_LENGTH(p_sessions_json);

    WHILE v_i < v_len DO
        SET v_sesiune_id = JSON_EXTRACT(p_sessions_json, CONCAT('$[', v_i, '].id_s'));

        SET v_status_programare = JSON_UNQUOTE(JSON_EXTRACT(p_sessions_json, CONCAT('$[', v_i, '].st')));

        INSERT INTO Programari (Data_si_ora, Status_confirmare, fk_idClientPr, fk_idSesiunePr)
        VALUES (NOW(), v_status_programare, p_id_client, v_sesiune_id);

        SET v_i = v_i + 1;
    END WHILE;

    SELECT v_abonament_id AS id_abonament;

END
-- PROC_END