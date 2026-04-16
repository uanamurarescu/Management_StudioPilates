
CREATE TABLE IF NOT EXISTS Clienti(
    ID_client INT AUTO_INCREMENT PRIMARY KEY,
    CNP VARCHAR(13) UNIQUE,
    Nume VARCHAR(25) NOT NULL,
    Prenume VARCHAR(25) NOT NULL,
    Varsta VARCHAR(3),
    Nivel_sedentarism VARCHAR(10) NOT NULL,
    Sesiune_dorita VARCHAR(100) NOT NULL
);
CREATE TABLE IF NOT EXISTS Antrenori(
    ID_antrenor INT AUTO_INCREMENT PRIMARY KEY,
    Nume VARCHAR(25) NOT NULL,
    Prenume VARCHAR(25) NOT NULL,
    Nivel_antrenamente VARCHAR(10) NOT NULL,
    Tip_antrenamente VARCHAR(100) NOT NULL,
    Scor_feedback INT NOT NULL
);

CREATE TABLE IF NOT EXISTS Sesiuni(
    ID_sesiune INT AUTO_INCREMENT PRIMARY KEY,
    Tip_pilates VARCHAR(100) NOT NULL,
    Tip_sesiune VARCHAR(10) NOT NULL ,
    Capacitate_maxima INT NOT NULL,
    Nivel_dificultate VARCHAR(10) NOT NULL,
    Durata VARCHAR(25) NOT NULL,
    Data_si_ora TIMESTAMP NOT NULL,
    fk_idAntrenorS INT,
    FOREIGN KEY (fk_idAntrenorS) REFERENCES Antrenori(ID_antrenor) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS userC(
    ID_user INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(25) NOT NULL,
    fk_idClient INT,
    FOREIGN KEY (fk_idClient) REFERENCES Clienti(ID_client) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS Abonamente(
    ID_abonament INT AUTO_INCREMENT PRIMARY KEY,
    Pret INT NOT NULL,
    Durata VARCHAR(10) NOT NULL,
    Activ VARCHAR(2) NOT NULL,
    fk_idClientA INT,
    fk_idSesiuneA INT,
    fk_idUser INT,
    FOREIGN KEY (fk_idClientA) REFERENCES Clienti(ID_client) ON DELETE CASCADE,
    FOREIGN KEY (fk_idSesiuneA) REFERENCES Sesiuni(ID_sesiune) ON DELETE CASCADE,
    FOREIGN KEY (fk_idUser) REFERENCES userC(ID_user) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS Plati(
    ID_plata INT AUTO_INCREMENT PRIMARY KEY,
    Data_si_ora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fk_idClientP INT,
    fk_idAbonamentP INT,
    FOREIGN KEY (fk_idClientP) REFERENCES Clienti(ID_client) ON DELETE CASCADE,
    FOREIGN KEY (fk_idAbonamentP) REFERENCES Abonamente(ID_abonament) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS Programari(
    ID_programare INT AUTO_INCREMENT PRIMARY KEY,
    Data_si_ora TIMESTAMP NOT NULL,
    Status_confirmare VARCHAR(15) NOT NULL,
    fk_idClientPr INT,
    fk_idSesiunePr INT,
    FOREIGN KEY (fk_idClientPr) REFERENCES Clienti(ID_client) ON DELETE CASCADE,
    FOREIGN KEY (fk_idSesiunePr) REFERENCES Sesiuni(ID_sesiune) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS Review(
    ID_review INT AUTO_INCREMENT PRIMARY KEY,
    Data_si_ora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    Comentariu VARCHAR(500),
    Nota_antrenor INT NOT NULL,
    fk_idClientR INT,
    fk_idAntrenorR INT,
    FOREIGN KEY (fk_idClientR) REFERENCES Clienti(ID_client) ON DELETE CASCADE,
    FOREIGN KEY (fk_idAntrenorR) REFERENCES Antrenori(ID_antrenor) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS Echipamente(
    ID_echipament INT AUTO_INCREMENT PRIMARY KEY,
    Denumire VARCHAR(100) NOT NULL,
    Stare_echipament VARCHAR(50) NOT NULL,
    Data_verificare_echipament TIMESTAMP NOT NULL,
    fk_idSesiuneE INT,
    fk_idAntrenorE INT,
    FOREIGN KEY (fk_idSesiuneE) REFERENCES Sesiuni(ID_sesiune) ON DELETE CASCADE,
    FOREIGN KEY (fk_idAntrenorE) REFERENCES Antrenori(ID_antrenor) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS user_log(
    ID_client INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    action VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES userC(ID_user) ON DELETE CASCADE
);