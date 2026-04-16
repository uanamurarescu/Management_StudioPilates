
DROP TRIGGER IF EXISTS trg_active_sub_before_insert;
--TRIGGER_END

CREATE TRIGGER trg_active_sub_before_insert
BEFORE INSERT ON Abonamente
FOR EACH ROW
BEGIN
    IF NEW.Activ NOT IN ('DA', 'NU') THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Eroare: Statusul abonamentului trebuie sa fie DA sau NU.';
    END IF;
END
--TRIGGER_END


DROP TRIGGER IF EXISTS trg_after_review_insert;
--TRIGGER_END

CREATE TRIGGER trg_after_review_insert
AFTER INSERT ON Review
FOR EACH ROW
BEGIN
    UPDATE Antrenori
    SET Scor_feedback = (
        SELECT AVG(Nota_antrenor)
        FROM Review
        WHERE fk_idAntrenorR = NEW.fk_idAntrenorR
    )
    WHERE ID_antrenor = NEW.fk_idAntrenorR;
END
--TRIGGER_END