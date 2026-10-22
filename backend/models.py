from datetime import date, datetime, time

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, Integer, String, Text, Time, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Utilisateur(Base):
    __tablename__ = "utilisateur"

    id_user: Mapped[int] = mapped_column(Integer, primary_key=True)
    nom_user: Mapped[str] = mapped_column(String(255), nullable=False)
    email_user: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    mdp_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    date_crea_user: Mapped[datetime | None] = mapped_column(
        DateTime, server_default=func.now()
    )

    disponibilites: Mapped[list["Disponibilite"]] = relationship(
        back_populates="utilisateur", passive_deletes=True
    )
    equipements_associes: Mapped[list["UtilisateurEquipement"]] = relationship(
        back_populates="utilisateur", passive_deletes=True
    )
    groupes_associes: Mapped[list["UtilisateurGroupe"]] = relationship(
        back_populates="utilisateur", passive_deletes=True
    )
    votes: Mapped[list["Vote"]] = relationship(
        back_populates="utilisateur", passive_deletes=True
    )


class Disponibilite(Base):
    __tablename__ = "disponibilite"

    id_dispo: Mapped[int] = mapped_column(Integer, primary_key=True)
    date_dispo: Mapped[date] = mapped_column(Date, nullable=False)
    heure_debut_dispo: Mapped[time] = mapped_column(Time, nullable=False)
    heure_fin_dispo: Mapped[time] = mapped_column(Time, nullable=False)
    statut: Mapped[str] = mapped_column(String(50), nullable=False)
    id_user: Mapped[int] = mapped_column(
        ForeignKey("utilisateur.id_user", ondelete="CASCADE"), nullable=False
    )

    utilisateur: Mapped["Utilisateur"] = relationship(back_populates="disponibilites")


class Equipement(Base):
    __tablename__ = "equipement"

    id_equipement: Mapped[int] = mapped_column(Integer, primary_key=True)
    nom_equipement: Mapped[str] = mapped_column(String(255), nullable=False)
    cat_equipement: Mapped[str | None] = mapped_column(String(255))

    utilisateurs_associes: Mapped[list["UtilisateurEquipement"]] = relationship(
        back_populates="equipement", passive_deletes=True
    )
    groupes_associes: Mapped[list["GroupeEquipement"]] = relationship(
        back_populates="equipement", passive_deletes=True
    )
    evenements_associes: Mapped[list["EvenementEquipement"]] = relationship(
        back_populates="equipement", passive_deletes=True
    )


class UtilisateurEquipement(Base):
    __tablename__ = "utilisateur_equipement"

    id_user: Mapped[int] = mapped_column(
        ForeignKey("utilisateur.id_user", ondelete="CASCADE"), primary_key=True
    )
    id_equipement: Mapped[int] = mapped_column(
        ForeignKey("equipement.id_equipement", ondelete="CASCADE"), primary_key=True
    )

    utilisateur: Mapped["Utilisateur"] = relationship(
        back_populates="equipements_associes"
    )
    equipement: Mapped["Equipement"] = relationship(
        back_populates="utilisateurs_associes"
    )


class Groupe(Base):
    __tablename__ = "groupe"

    id_grp: Mapped[int] = mapped_column(Integer, primary_key=True)
    nom_grp: Mapped[str] = mapped_column(String(255), nullable=False)
    description_grp: Mapped[str | None] = mapped_column(Text)
    url_photo: Mapped[str | None] = mapped_column(String(255))
    date_crea_grp: Mapped[datetime | None] = mapped_column(
        DateTime, server_default=func.now()
    )

    equipements_associes: Mapped[list["GroupeEquipement"]] = relationship(
        back_populates="groupe", passive_deletes=True
    )
    membres_associes: Mapped[list["UtilisateurGroupe"]] = relationship(
        back_populates="groupe", passive_deletes=True
    )
    repertoires: Mapped[list["Repertoire"]] = relationship(
        back_populates="groupe", passive_deletes=True
    )
    evenements_associes: Mapped[list["GroupeEvenement"]] = relationship(
        back_populates="groupe", passive_deletes=True
    )


class GroupeEquipement(Base):
    __tablename__ = "groupe_equipement"

    id_grp: Mapped[int] = mapped_column(
        ForeignKey("groupe.id_grp", ondelete="CASCADE"), primary_key=True
    )
    id_equipement: Mapped[int] = mapped_column(
        ForeignKey("equipement.id_equipement", ondelete="CASCADE"), primary_key=True
    )

    groupe: Mapped["Groupe"] = relationship(back_populates="equipements_associes")
    equipement: Mapped["Equipement"] = relationship(
        back_populates="groupes_associes"
    )


class UtilisateurGroupe(Base):
    __tablename__ = "utilisateur_groupe"

    id_user: Mapped[int] = mapped_column(
        ForeignKey("utilisateur.id_user", ondelete="CASCADE"), primary_key=True
    )
    id_grp: Mapped[int] = mapped_column(
        ForeignKey("groupe.id_grp", ondelete="CASCADE"), primary_key=True
    )
    role: Mapped[str | None] = mapped_column(String(100))
    date_rejoint: Mapped[datetime | None] = mapped_column(
        DateTime, server_default=func.now()
    )

    utilisateur: Mapped["Utilisateur"] = relationship(
        back_populates="groupes_associes"
    )
    groupe: Mapped["Groupe"] = relationship(back_populates="membres_associes")


class Repertoire(Base):
    __tablename__ = "repertoire"

    id_rep: Mapped[int] = mapped_column(Integer, primary_key=True)
    nom_rep: Mapped[str] = mapped_column(String(255), nullable=False)
    id_grp: Mapped[int] = mapped_column(
        ForeignKey("groupe.id_grp", ondelete="CASCADE"), nullable=False
    )

    groupe: Mapped["Groupe"] = relationship(back_populates="repertoires")
    evenements: Mapped[list["Evenement"]] = relationship(
        back_populates="repertoire", passive_deletes=True
    )
    morceaux_associes: Mapped[list["RepertoireMorceau"]] = relationship(
        back_populates="repertoire", passive_deletes=True
    )


class Evenement(Base):
    __tablename__ = "evenement"

    id_event: Mapped[int] = mapped_column(Integer, primary_key=True)
    titre_event: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str | None] = mapped_column(String(100))
    date_event: Mapped[date | None] = mapped_column(Date)
    heure_debut_event: Mapped[time | None] = mapped_column(Time)
    heure_fin_event: Mapped[time | None] = mapped_column(Time)
    lieu_event: Mapped[str | None] = mapped_column(String(255))
    id_rep: Mapped[int | None] = mapped_column(
        ForeignKey("repertoire.id_rep", ondelete="SET NULL")
    )

    repertoire: Mapped["Repertoire | None"] = relationship(back_populates="evenements")
    groupes_associes: Mapped[list["GroupeEvenement"]] = relationship(
        back_populates="evenement", passive_deletes=True
    )
    equipements_associes: Mapped[list["EvenementEquipement"]] = relationship(
        back_populates="evenement", passive_deletes=True
    )


class GroupeEvenement(Base):
    __tablename__ = "groupe_evenement"

    id_grp: Mapped[int] = mapped_column(
        ForeignKey("groupe.id_grp", ondelete="CASCADE"), primary_key=True
    )
    id_event: Mapped[int] = mapped_column(
        ForeignKey("evenement.id_event", ondelete="CASCADE"), primary_key=True
    )

    groupe: Mapped["Groupe"] = relationship(back_populates="evenements_associes")
    evenement: Mapped["Evenement"] = relationship(back_populates="groupes_associes")


class EvenementEquipement(Base):
    __tablename__ = "evenement_equipement"

    id_event: Mapped[int] = mapped_column(
        ForeignKey("evenement.id_event", ondelete="CASCADE"), primary_key=True
    )
    id_equipement: Mapped[int] = mapped_column(
        ForeignKey("equipement.id_equipement", ondelete="CASCADE"), primary_key=True
    )

    evenement: Mapped["Evenement"] = relationship(
        back_populates="equipements_associes"
    )
    equipement: Mapped["Equipement"] = relationship(
        back_populates="evenements_associes"
    )


class Morceau(Base):
    __tablename__ = "morceau"

    id_song: Mapped[int] = mapped_column(Integer, primary_key=True)
    titre_song: Mapped[str] = mapped_column(String(255), nullable=False)
    compositeur: Mapped[str | None] = mapped_column(String(255))
    lien_youtube: Mapped[str | None] = mapped_column(String(255))
    url_img: Mapped[str | None] = mapped_column(String(255))
    date_crea_song: Mapped[datetime | None] = mapped_column(
        DateTime, server_default=func.now()
    )

    repertoires_associes: Mapped[list["RepertoireMorceau"]] = relationship(
        back_populates="morceau", passive_deletes=True
    )
    votes: Mapped[list["Vote"]] = relationship(
        back_populates="morceau", passive_deletes=True
    )


class RepertoireMorceau(Base):
    __tablename__ = "repertoire_morceau"

    id_rep: Mapped[int] = mapped_column(
        ForeignKey("repertoire.id_rep", ondelete="CASCADE"), primary_key=True
    )
    id_song: Mapped[int] = mapped_column(
        ForeignKey("morceau.id_song", ondelete="CASCADE"), primary_key=True
    )
    position: Mapped[int | None] = mapped_column(Integer)

    repertoire: Mapped["Repertoire"] = relationship(
        back_populates="morceaux_associes"
    )
    morceau: Mapped["Morceau"] = relationship(back_populates="repertoires_associes")


class Vote(Base):
    __tablename__ = "vote"
    __table_args__ = (CheckConstraint("note >= 0 AND note <= 5"),)

    id_vote: Mapped[int] = mapped_column(Integer, primary_key=True)
    note: Mapped[int | None] = mapped_column(Integer)
    id_user: Mapped[int] = mapped_column(
        ForeignKey("utilisateur.id_user", ondelete="CASCADE"), nullable=False
    )
    id_song: Mapped[int] = mapped_column(
        ForeignKey("morceau.id_song", ondelete="CASCADE"), nullable=False
    )

    utilisateur: Mapped["Utilisateur"] = relationship(back_populates="votes")
    morceau: Mapped["Morceau"] = relationship(back_populates="votes")


__all__ = [
    "Base",
    "Disponibilite",
    "Equipement",
    "Evenement",
    "EvenementEquipement",
    "Groupe",
    "GroupeEquipement",
    "GroupeEvenement",
    "Morceau",
    "Repertoire",
    "RepertoireMorceau",
    "Utilisateur",
    "UtilisateurEquipement",
    "UtilisateurGroupe",
    "Vote",
]
