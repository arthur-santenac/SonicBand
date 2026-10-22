CREATE TABLE Utilisateur (
    id_user SERIAL PRIMARY KEY,
    nom_user VARCHAR(255) NOT NULL,
    email_user VARCHAR(255) UNIQUE NOT NULL,
    mdp_hash VARCHAR(255) NOT NULL,
    date_crea_user TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Disponibilite (
    id_dispo SERIAL PRIMARY KEY,
    date_dispo DATE NOT NULL,
    heure_debut_dispo TIME NOT NULL,
    heure_fin_dispo TIME NOT NULL,
    statut VARCHAR(50) NOT NULL,
    id_user INT NOT NULL,
    FOREIGN KEY (id_user) REFERENCES Utilisateur(id_user) ON DELETE CASCADE
);

CREATE TABLE Equipement (
    id_equipement SERIAL PRIMARY KEY,
    nom_equipement VARCHAR(255) NOT NULL,
    cat_equipement VARCHAR(255)
);

CREATE TABLE Utilisateur_Equipement (
    id_user INT NOT NULL,
    id_equipement INT NOT NULL,
    PRIMARY KEY (id_user, id_equipement),
    FOREIGN KEY (id_user) REFERENCES Utilisateur(id_user) ON DELETE CASCADE,
    FOREIGN KEY (id_equipement) REFERENCES Equipement(id_equipement) ON DELETE CASCADE
);

CREATE TABLE Groupe (
    id_grp SERIAL PRIMARY KEY,
    nom_grp VARCHAR(255) NOT NULL,
    description_grp TEXT,
    url_photo VARCHAR(255),
    date_crea_grp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Groupe_Equipement (
    id_grp INT NOT NULL,
    id_equipement INT NOT NULL,
    PRIMARY KEY (id_grp, id_equipement),
    FOREIGN KEY (id_grp) REFERENCES Groupe(id_grp) ON DELETE CASCADE,
    FOREIGN KEY (id_equipement) REFERENCES Equipement(id_equipement) ON DELETE CASCADE
);

CREATE TABLE Utilisateur_Groupe (
    id_user INT NOT NULL,
    id_grp INT NOT NULL,
    role VARCHAR(100),
    date_rejoint TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id_user, id_grp),
    FOREIGN KEY (id_user) REFERENCES Utilisateur(id_user) ON DELETE CASCADE,
    FOREIGN KEY (id_grp) REFERENCES Groupe(id_grp) ON DELETE CASCADE
);

CREATE TABLE Repertoire (
    id_rep SERIAL PRIMARY KEY,
    nom_rep VARCHAR(255) NOT NULL,
    id_grp INT NOT NULL,
    FOREIGN KEY (id_grp) REFERENCES Groupe(id_grp) ON DELETE CASCADE
);

CREATE TABLE Evenement (
    id_event SERIAL PRIMARY KEY,
    titre_event VARCHAR(255) NOT NULL,
    type VARCHAR(100),
    date_event DATE,
    heure_debut_event TIME,
    heure_fin_event TIME,
    lieu_event VARCHAR(255),
    id_rep INT,
    FOREIGN KEY (id_rep) REFERENCES Repertoire(id_rep) ON DELETE SET NULL
);

CREATE TABLE Groupe_Evenement (
    id_grp INT NOT NULL,
    id_event INT NOT NULL,
    PRIMARY KEY (id_grp, id_event),
    FOREIGN KEY (id_grp) REFERENCES Groupe(id_grp) ON DELETE CASCADE,
    FOREIGN KEY (id_event) REFERENCES Evenement(id_event) ON DELETE CASCADE
);

CREATE TABLE Evenement_Equipement (
    id_event INT NOT NULL,
    id_equipement INT NOT NULL,
    PRIMARY KEY (id_event, id_equipement),
    FOREIGN KEY (id_event) REFERENCES Evenement(id_event) ON DELETE CASCADE,
    FOREIGN KEY (id_equipement) REFERENCES Equipement(id_equipement) ON DELETE CASCADE
);

CREATE TABLE Morceau (
    id_song SERIAL PRIMARY KEY,
    titre_song VARCHAR(255) NOT NULL,
    compositeur VARCHAR(255),
    lien_youtube VARCHAR(255),
    url_img VARCHAR(255),
    date_crea_song TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Repertoire_Morceau (
    id_rep INT NOT NULL,
    id_song INT NOT NULL,
    position INT,
    PRIMARY KEY (id_rep, id_song),
    FOREIGN KEY (id_rep) REFERENCES Repertoire(id_rep) ON DELETE CASCADE,
    FOREIGN KEY (id_song) REFERENCES Morceau(id_song) ON DELETE CASCADE
);

CREATE TABLE Vote (
    id_vote SERIAL PRIMARY KEY,
    note INT CHECK (note >= 0 AND note <= 5),
    id_user INT NOT NULL,
    id_song INT NOT NULL,
    FOREIGN KEY (id_user) REFERENCES Utilisateur(id_user) ON DELETE CASCADE,
    FOREIGN KEY (id_song) REFERENCES Morceau(id_song) ON DELETE CASCADE
);