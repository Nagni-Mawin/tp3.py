import csv
import json
taux_tax=0.15
from datetime import datetime

def charger_clients():
    clients={}
    try:
        with open("clients.csv", "r", encoding="utf-8") as fichier_clients:
            #lire le ficher clients.csv et le convertir en dictionnaire
            lecteur_clients=csv.DictReader(fichier_clients)
            #parcourir chaque ligne du fichier
            for ligne in lecteur_clients:
                #recuperer l'ID du client et le convertir en entier
                id_client=int(ligne["id_client"])
                #ajout du client au dictionnaire avec son ID
                clients[id_client]=ligne
        return clients
    except FileNotFoundError:
        print("Fichier clients introuvable")
        return {}
    
def charger_articles():
    try:
        with open("articles.json","r",encoding="utf-8") as fichier_articles:
            liste = json.load(fichier_articles)
            return {art['id']: art for art in liste}  
    except FileNotFoundError:
        print("Fichier articles introuvable")  
        #retourne le dictionnaire vide si le ficher n'est pas trouvé  
        return {}
def charger_achats():
    achats=[]
    try:
        with open("achats.csv","r",encoding="utf-8") as ficher_achats:
            lecteur_achats=csv.DictReader(ficher_achats)
            for ligne in lecteur_achats:
              #ajout de l'achat a la liste achats
              achats.append(ligne)
        return achats
    except FileNotFoundError:
        print("Fichier achats introuvable")
        #retourne la liste vide si le ficher n'est pas trouvé
        return []
def parser_articles(chaine_articles):
    resultat=[]
    segments=chaine_articles.split(";")
    for segment in segments:
        if ":" in segment:
            try: 
                id_article , quantite = segment.split(":")
                resultat.append({"id" : int(id_article.strip()), "quantite" : int(quantite.strip())})
            except ValueError:
                continue
                #print(f"Erreur dans les données d'article : {segment} ignoré ")
        elif segment.strip():
            continue
            #print(f"Segment mal formé  : {segment} ignoré")
    return resultat
def calculer_totaux(achat,dictionnaire_articles):
    sous_total=0
    details_articles=[]
    liste_article=parser_articles(achat['articles'])
    for article in liste_article:
        info_article=dictionnaire_articles.get(article['id'])
        if info_article:
            try:
                total_ligne=info_article['prix'] * article['quantite']
                sous_total+=total_ligne
            except (ValueError,TypeError):
                #Ignorer un article si son prix ou sa quantité est invalide
                continue
            details_articles.append({
                "nom": info_article['nom'],
                "quantite" : article['quantite'],
                "prix_unitaire": info_article['prix'],
                "total_ligne": total_ligne
            })
            #formule
    taxes = sous_total * taux_tax
    #Gestion d'erreur dans remise
    try:
        remise_taux = float(achat['remise'])
    except (ValueError,TypeError):
        remise_taux=0
    montant_remise = sous_total * (remise_taux / 100)
    total_final = sous_total - montant_remise + taxes
    return {
        "sous_total": round(sous_total, 2),
        "taxes": round(taxes, 2),
        "remise_montant": round(montant_remise, 2),
        "total_final": round(total_final, 2),
        "details": details_articles
    }
def afficher_transactions(achats,clients,articles):
    print("-----Liste des transactions valides------")
    for achat in achats:
        if achat['statut'].strip().lower()=="complete":
            client=clients.get(int(achat['id_client']),{"nom" : "Inconnu", "ville" : "Inconnu"})
            totaux=calculer_totaux(achat,articles)
            
            print(f"\nID: {achat['id_transaction']} | Date: {achat['date']} | Client: {client['nom']} ({client['ville']})")
            for detail in totaux['details']:
                print(f"  - {detail['nom']}: x{detail['quantite']} : {detail['total_ligne']:.2f}$")
            print(f"  - Sous-total: {totaux['sous_total']}$ | Remise: {achat['remise']}% | Taxes: {totaux['taxes']}$")
            print(f"  - TOTAL FINAL: {totaux['total_final']}$")
            print("-" * 50)
def afficher_statistiques(achats,clients,articles):
    total_ventes = 0
    nombre_transaction_valides = 0
    depenses_clients = {} #total depenses par client
    #Dictionnaire pour stocker le total vendeu par article (id_article : quantite_vendue)
    quantite_total_articles_vendu = {} 
    revenu_article_vendu = {} #revenu total par article (id_article : revenu_total)
    for achat in achats:#parcourir les achats pour calculer les statistiques
        if achat['statut'].strip().lower()=="complete": #verifier si la transaction est valide
            nombre_transaction_valides+=1 #incremente le compteur de transactions valides
            try:
                
                id_client=int(achat['id_client']) #recuperer l'ID du client et le convertir en entier
            except (ValueError, TypeError):
                print(f"Erreur dans les données du client pour la transaction {achat['id_transaction']} : ignoré")
                continue
            totaux=calculer_totaux(achat,articles) #calculer les totaux
            total_ventes+=totaux['total_final'] #incremente le total global des ventes avec le total final de la transaction
            #
            depenses_clients[id_client] = depenses_clients.get(id_client, 0) + totaux['total_final'] #depense par client en cumulant le total final de chaque transaction valide pour ce client
            
            liste_articles=parser_articles(achat['articles']) #parser la liste des articles de la transaction pour calculer les statistiques par article
            for artic in liste_articles:
                try:
                    id_article=int(artic['id'])
                    quantite_article=int(artic['quantite'])
                    #if id_article not in articles:
                     #   print(f"Article ID {id_article} non trouvé dans le dictionnaire des articles : ignoré")
                           #  continue
                except (ValueError,TypeError):
                    print(f"Erreur dans les données de l'article ID {artic['id']} : ignoré")
                    continue
                info_article=articles.get(id_article)
                if not info_article:
                    print(f"Article ID {id_article} non trouvé dans le dictionnaire des articles : ignoré")
                    continue
                try:
                    prix_unitaire=float(info_article.get('prix', 0))
                except (ValueError,TypeError):
                    print(f"Erreur dans le prix de l'article ID {id_article} : ignoré")
                    continue
                quantite_total_articles_vendu[id_article] = quantite_total_articles_vendu.get(id_article, 0) + quantite_article
                #if id_article in articles:
                revenu_article_vendu[id_article] = revenu_article_vendu.get(id_article, 0) + (quantite_article * prix_unitaire)
    #affiche les statistiques globales
    print("\n--- STATISTIQUES GLOBALES ---")
    print(f"-Total global des ventes : {round(total_ventes, 2)}$")
    print(f"-Nombre de transactions valides : {nombre_transaction_valides}")
    if depenses_clients:
        vip_id=max(depenses_clients,key=depenses_clients.get)
        nom_client_vip=clients.get(vip_id,{}).get('nom')
        if not nom_client_vip or nom_client_vip.strip() == "":
            nom_client_vip="Inconnu"
        print(f"-Client VIP : {nom_client_vip} : ({round(depenses_clients[vip_id],2)}$)")
    if quantite_total_articles_vendu:
        id_article_vendu_plus=max(quantite_total_articles_vendu, key=quantite_total_articles_vendu.get)
        
        nom_article_le_plus_vendu=articles.get(id_article_vendu_plus,{}).get('nom')
        if not nom_article_le_plus_vendu or nom_article_le_plus_vendu.strip() == "":
            nom_article_le_plus_vendu="Inconnu"
        print(f"-L'article le plus vendu est : {nom_article_le_plus_vendu}")
        id_article_rentable=max(revenu_article_vendu,key=revenu_article_vendu.get)
        nom_article_rentable=articles.get(id_article_rentable,{}).get('nom')
        if not nom_article_rentable or nom_article_rentable.strip() == "":
            nom_article_rentable="Inconnu"
        print(f"-L'article le plus rentable est : {nom_article_rentable}")
    print("-MONTANT DEPENSES PAR CLIENT: ")
    for id_client in sorted(depenses_clients.keys()):
        montant=depenses_clients[id_client]
        nom_client=clients.get(id_client,{}).get('nom')
        if not nom_client or nom_client.strip() == "":
            nom_client="Inconnu"
        print(f"-{nom_client} ---> {round(montant,2)}$")
def client_plus_transaction(achats,clients):
    compteur={}
    for achat in achats:
        if achat['statut'].strip().lower()=="complete":
            id_client=int(achat['id_client'])
            if id_client in compteur:
                compteur[id_client]+=1
            else:
                compteur[id_client]=1
            #compteur[id_client]=compteur.get(id_client, 0) + 1
    if compteur:
        id_max=max(compteur , key=compteur.get)
        print("Le Client ayant effectué le plus de transactions est : ")
        print(f"{clients[id_max]['nom']} ({compteur[id_max]} transactions)")
        
def transaction_la_plus_chere(achats):
    total_max=0
    transaction_max=None
    
    for achat in achats:
        if achat['statut'].strip().lower()=="complete":
            #totaux=calculer_totaux(achat,articles)
            if achat.get('total_final', 0) > total_max:
                total_max=achat['total_final']
                transaction_max=achat
    if transaction_max:
        print(f"\nTransaction la plus chère : \nID : {transaction_max['id_transaction']} | Date : {transaction_max['date']} | Montant : {round(total_max,2)}$")
def filtrer_par_methode_paiement(achats):
    while True:
        print("" + "-"*30)
        print("   Methodes de paiement")
        print("-"*30)
        print(" 1. Carte")
        print(" 2. Especes")
        print(" 3. Virement")
        print(" 4. Tous")
        print(" 5. Retour")
        choix_methode=input("\nVotre choix : ")
        if choix_methode=="1":
            print(f"\nTRANSACTIONS PAR CARTE")
            print("  ID\t|Date\t     |Methode\t       |ID Client   |Articles")
            print("-" *66)
            for achat in achats:
                if achat['methode_paiement'].strip().lower()=="carte" and achat['statut'].strip().lower()=="complete":
                    print(f"- {achat['id_transaction']} \t| {achat['date']:<10} | {achat['methode_paiement']:<15} | {achat['id_client']:<10} | {achat['articles']}")
            print("-" *66)
        elif choix_methode=="2":
            print(f"\nTRANSACTIONS EN ESPECES")
            print("  ID\t|Date\t     |Methode\t       |ID Client   |Articles")
            print("-" *66)
            for achat in achats:
                if achat['methode_paiement'].strip().lower()=="especes" and achat['statut'].strip().lower()=="complete":
                    print(f"- {achat['id_transaction']} \t| {achat['date']:<10} | {achat['methode_paiement']:<15} | {achat['id_client']:<10} | {achat['articles']}")
            print("-" *66)
        elif choix_methode=="3":
            print("\nTRANSACTION PAR VIREMENT")
            print("  ID\t|Date\t     |Methode\t       |ID Client   |Articles")
            print("-" *66)
            for achat in achats:
                if achat ['methode_paiement'].strip().lower()=="virement" and achat['statut'].strip().lower()=="complete":
                    print(f"- {achat['id_transaction']} \t| {achat['date']:<10} | {achat['methode_paiement']:<15} | {achat['id_client']:<10} | {achat['articles']}")
            print("-" *66)
        elif choix_methode == "4":
            print("\nTOUTES LES TRANSACTIONS") 
            print("  ID\t|Date\t     |Methode\t       |ID Client   |Articles")
            print("-" *66)
            for achat in achats:
                if achat['statut'].strip().lower()=="complete":
                    print(f"- {achat['id_transaction']} \t| {achat['date']:<10} | {achat['methode_paiement']:<15} | {achat['id_client']:<10} | {achat['articles']}")
            print("-" *66)
        elif choix_methode=="5":
            break
        else:
            print("Choix invalide!")
def trier_transaction_par_date(achats):
    transaction_valide=[
        achat for achat in achats
        if achat['statut'].strip().lower()=="complete"
    ]
    transactions_triees= sorted(transaction_valide,key=lambda x :datetime.strptime(x['date'], "%Y-%m-%d"))
    print("\nTRANSACTION TIREE PAR DATE")
    print(" |Date\t        |ID Transaction\t  |ID Client   |Articles")
    print("-" *60)
    for achat in transactions_triees:
        print(f"- {achat['date']} \t| {achat['id_transaction']:<15} | {achat['id_client']:<10} | {achat['articles']}")
    print("-" *60)
def generer_rapport(achats, clients, articles, nom_fichier="rapport.txt"):
    with open(nom_fichier, "w", encoding="utf-8") as f:
        f.write("=== RAPPORT DES TRANSACTIONS ===\n\n")
        
        # Transactions valides
        f.write("----- TANSACTIONS VALIDES -----\n")
        for achat in achats:
            if achat['statut'].strip().lower() == "complete":
                nom_client = clients.get(int(achat['id_client']), {"nom": "Inconnu", "ville": "Inconnu"})
                totaux = calculer_totaux(achat, articles)
                f.write(f"\nID: {achat['id_transaction']} | Date: {achat['date']} | Client: {nom_client['nom']} ({nom_client['ville']})\n")
                for detail in totaux['details']:
                    f.write(f"  -Nom : {detail['nom']} | Quantité: {detail['quantite']} | Total: {detail['total_ligne']:.2f}$\n")
                f.write(f"  - Sous-total: {totaux['sous_total']}$ | Remise: {achat['remise']}% | Taxes: {totaux['taxes']}$\n")
                f.write(f"  - TOTAL FINAL: {totaux['total_final']}$\n")
                f.write("-" * 50 + "\n")
        
        # Statistiques globales
        total_ventes = 0
        depenses_clients = {}
        quantite_total_articles_vendu = {}
        revenu_article_vendu = {}

        for achat in achats:
            if achat['statut'].strip().lower() == "complete":
                totaux = calculer_totaux(achat, articles)
                total_ventes += totaux['total_final']
                id_client = int(achat['id_client'])
                depenses_clients[id_client] = depenses_clients.get(id_client, 0) + totaux['total_final']
                for artic in parser_articles(achat['articles']):
                    id_article = artic['id']
                    quantite_article=artic['quantite']
                    quantite_total_articles_vendu[id_article] = quantite_total_articles_vendu.get(id_article, 0) + quantite_article
                    if id_article in articles:
                        try:
                            prix_unitaire=float(articles.get(id_article,{}).get('prix', 0))
                            revenu_article_vendu[id_article] = revenu_article_vendu.get(id_article, 0) + (quantite_article * prix_unitaire)
                        except (ValueError, TypeError):
                            continue

        f.write("\n--- STATISTIQUES GLOBALES ---\n")
        f.write(f"- Total global des ventes : {round(total_ventes, 2)}$\n")
        f.write(f"- Nombre de transactions valides : {len(depenses_clients)}\n")
        

        if depenses_clients:
            vip_id = max(depenses_clients, key=depenses_clients.get)
            f.write(f"- Client VIP : {clients.get(vip_id, {}).get('nom', 'Inconnu')} ({round(depenses_clients.get(vip_id, 0),2)}$)\n")

        if quantite_total_articles_vendu:
            id_article_vendu_plus = max(quantite_total_articles_vendu, key=quantite_total_articles_vendu.get)
            nom_article = articles.get(id_article_vendu_plus, {}).get("nom", "Inconnu")
            if nom_article.strip() == "":
                nom_article = "Inconnu"
            f.write(f"- L'article le plus vendu est : {nom_article}\n")
            nom_article_rentable = articles.get(max(revenu_article_vendu, key=revenu_article_vendu.get), {}).get("nom", "Inconnu")
            if nom_article_rentable.strip() == "":
                nom_article_rentable = "Inconnu"
            id_article_rentable = max(revenu_article_vendu, key=revenu_article_vendu.get)
            f.write(f"- L'article le plus rentable est : {articles.get(id_article_rentable, {}).get('nom', 'Inconnu')}\n")

        f.write("\n- MONTANT DEPENSE PAR CLIENT \n")
        for id_client in sorted(depenses_clients.keys()):
            montant = depenses_clients[id_client]
            nom_client = clients.get(id_client, {}).get("nom", "Inconnu")
            if nom_client.strip() == "":
                nom_client = "Inconnu"
            f.write(f"  - {nom_client} ---> {round(montant,2)}$\n")
        f.write(f"\nTRANSACTIONS PAR CARTE\n\n")
        f.write("  ID\t|Date\t     |Methode\t       |ID Client   |Articles\n")
        #f.write("  ID\t\t|Date\t\t     |Methode\t\t       |ID Client   |Articles\n")
        f.write("------------------------------------------------------------------\n")
        for achat in achats:
            if achat['methode_paiement'].strip().lower()=="carte" and achat['statut'].strip().lower()=="complete":
                f.write(f"- {achat['id_transaction']} \t| {achat['date']:<10} | {achat['methode_paiement']:<15} | {achat['id_client']:<10} | {achat['articles']}\n")
        f.write("------------------------------------------------------------------\n")
        f.write(f"\nTRANSACTIONS EN ESPECE\n\n")
        f.write("  ID\t\t|Date\t\t     |Methode\t\t       |ID Client   |Articles\n")
        f.write("------------------------------------------------------------------\n")
        for achat in achats:
            if achat['methode_paiement'].strip().lower()=="especes" and achat['statut'].strip().lower()=="complete":
                f.write(f"- {achat['id_transaction']} \t| {achat['date']:<10} | {achat['methode_paiement']:<15} | {achat['id_client']:<10} | {achat['articles']}\n")
        f.write("------------------------------------------------------------------\n")
        f.write(f"\nTRANSACTIONS PAR VIREMENT \n\n")
        f.write("  ID\t\t|Date\t\t     |Methode\t\t       |ID Client   |Articles\n")
        f.write("------------------------------------------------------------------\n")
        for achat in achats:
            if achat ['methode_paiement'].strip().lower()=="virement" and achat['statut'].strip().lower()=="complete":
                f.write(f"- {achat['id_transaction']} \t| {achat['date']:<10} | {achat['methode_paiement']:<15} | {achat['id_client']:<10} | {achat['articles']}\n")
        f.write("------------------------------------------------------------------\n")

    print(f"Rapport généré avec succès dans le fichier '{nom_fichier}'")
        #Menu interactif
def menu():
    print(f"\n--- Bienvenue dans le système de gestion des transactions ---")
    clients = charger_clients()
    articles = charger_articles()
    achats = charger_achats()
    print(f"{len(achats)} transactions chargées.")
    for achat in achats:
        if achat ['statut'].strip().lower()=="complete":
            totaux=calculer_totaux(achat,articles)
            achat['total_final']=totaux['total_final']
    while True:
        #print("\nBienvenu  ")
        print("" + "="*30)
        print("      MENU PRINCIPAL")
        print("="*30)
        print("1. Afficher les transactions valides")
        print("2. Afficher les statistiques globales")
        print("3. Analyse avancée")
        print("4. Générer un rapport")
        print("5. Quitter")
        
        choix = input("\nVotre choix : ")
        if choix=="1":
            afficher_transactions(achats,clients,articles)
        elif choix == "2":
            afficher_statistiques(achats, clients, articles)
        elif choix == "3":
            #menu des methodes de paiement
            while True:
                print("" + "-"*30)
                print("   Recherches avancées")
                print("-"*30)
                print(" 1. Client ayant effectué plus de transactions")
                print(" 2. Transaction la plus chère ")
                print(" 3. Filtrer par methode de paiement")
                print(" 4. Trier par date ")
                print(" 5. Retour ")
                choix2=input("\nEntrez votre choix : ")
                if choix2 == "1":
                    client_plus_transaction(achats,clients)
                elif choix2=="2":
                    transaction_la_plus_chere(achats)
                elif choix2 == "3":
                    filtrer_par_methode_paiement(achats)
                elif choix2 == "4":
                    trier_transaction_par_date(achats)
                elif choix2 == "5":
                    break
                else:
                    print("Choix invalide ! ")
                    
        elif choix == "4":
            generer_rapport(achats, clients, articles)
        elif choix == "5":
            print("Au revoir !")
            break
        else:
            print("Choix invalide")
if __name__ == "__main__":
    menu()
