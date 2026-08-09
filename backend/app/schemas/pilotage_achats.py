from datetime import date,datetime
from decimal import Decimal
from pydantic import BaseModel
class KpiAchatsRead(BaseModel):
    commandes_ouvertes:int;commandes_en_retard:int;livraisons_30_jours:int;montant_engage_ht:Decimal;articles_sans_fournisseur:int;articles_sans_tarif:int;otd_global_pct:Decimal|None
class CommandeAlerteRead(BaseModel):
    id:int;reference:str;fournisseur:str;statut:str;date_livraison_prevue:date|None;jours_retard:int;montant_restant_ht:Decimal
class LivraisonAttendueRead(BaseModel):
    commande_id:int;reference:str;fournisseur:str;date_livraison_prevue:date|None;statut:str;montant_restant_ht:Decimal
class PerformanceFournisseurRead(BaseModel):
    fournisseur_id:int;code:str;raison_sociale:str;commandes:int;commandes_evaluees_otd:int;commandes_a_lheure:int;otd_pct:Decimal|None;retard_moyen_jours:Decimal|None;montant_commande_ht:Decimal;montant_restant_ht:Decimal;commandes_en_retard:int
class EvolutionPrixRead(BaseModel):
    article_fournisseur_id:int;article_reference:str;article_designation:str;fournisseur_code:str;fournisseur:str;prix_actuel:Decimal|None;prix_precedent:Decimal|None;variation_pct:Decimal|None;date_dernier_prix:datetime|None
class ArticleCritiqueRead(BaseModel):
    article_id:int;reference:str;designation:str;fournisseur_prefere:str|None;prix_unitaire_ht:Decimal|None;delai_jours:int|None;anomalies:list[str]
class EcartReceptionRead(BaseModel):
    commande_id:int;commande_reference:str;fournisseur:str;article_reference:str;article_designation:str;quantite_commandee:Decimal;quantite_recue:Decimal;ecart_quantite:Decimal;unite:str;date_reception_finale:datetime|None
class DashboardAchatsRead(BaseModel):
    kpis:KpiAchatsRead;retards:list[CommandeAlerteRead];livraisons:list[LivraisonAttendueRead];fournisseurs:list[PerformanceFournisseurRead];prix:list[EvolutionPrixRead];articles_critiques:list[ArticleCritiqueRead];ecarts_reception:list[EcartReceptionRead]
