import os
import random
import math
import re
import pickle

os.chdir(os.getcwd())


# ---- "MACHINE LEARNING" ---- #


def recolteDonnees(nom_fichier, nb_parties=20): 
	""" Fonction permettant la récolte de données afin de les exploiter pour le machine learning de l'ordinateur."""
	with open(nom_fichier, "w") as f: # on commence par créer le fichier
		pass 
	for i in range(nb_parties): 
		jeu = ModeMachineLearning(0, ["Ordi 1", "Ordi 2"], 30, "data_bot", 1, 2)
		while(jeu.fin_de_partie != True): # déroulement normal de la partie
			jeu.gestionTour()
		with open(nom_fichier, "a") as f:
			f.write(jeu.log_o1)
			f.write(jeu.log_o2)
	return None


def analyseDonnees(nom_fichier_a_analyser = "log_bot.txt", nom_fichier_a_creer = "data_bot"):
	""" Fonction qui analyse les résultats et crée des statistiques pour chaque coup qui a été joué dans les données récoltées. """
	"""
	On liste nos statistiques (comprises entre 0 et 1) avec un dictionnaire agencé comme suit : 
	{
	[allumettes_restantes, nb_a_retirer] : statistique de victoire,
	[allumettes_restantes_bis, nb_a_retirer_bis] : statistique de victoire_bis,
	[combinaison] : stat, 
	Ce dictionnaire est d'abord enregistré de sous la forme :
	{
	[combinaison] : [nb_victoire, nb_occurence]
	}
	}
	"""
	tableau_stats = {}
	with open(nom_fichier_a_analyser, "r") as f: 
		for line in f:
			pattern = r"(?P<combinaison>[0-9]+ - [0-9]+) --> (?P<resultat>V?D?)"
			match = re.search(pattern, line)
			combinaison = match.group("combinaison")
			resultat = match.group("resultat")
			if(resultat == "V"): # une victoire   
				stats_combinaison = [1, 1]
			else:
				stats_combinaison = [0, 1]
			if(combinaison in tableau_stats): # la combinaison existe déjà donc on additionne les stats déjà associées à cette combinaison et les stats de la combinaison à l'itération actuelle.
				tableau_stats[combinaison] = [tableau_stats[combinaison][0] + stats_combinaison[0], tableau_stats[combinaison][1] + stats_combinaison[1]]
			else:
				tableau_stats[combinaison] = stats_combinaison
	for i in tableau_stats.keys(): # pour chaque clé on doit transformer le nombre de victoire et le nombre d'occurence en une statistique comprise entre 0 et 1
		tableau_stats[i] = round(tableau_stats[i][0] / tableau_stats[i][1], 4) # [0] : nb de victoires, [1] : nb d'occurence total, et on arrondit à 4 chiffres le résultat
	with open(nom_fichier_a_creer, "wb") as f: # enregistrement du tableau des statistiques EN BINAIRE car pickle
		pickle.Pickler(f).dump(tableau_stats)
	return None


# ---- LE JEU ---- #


class Allumette:
	""" La classe qui permet de gérer les allumettes et leurs méthodes."""
	def __init__(self, nb_joueurs, liste_participant, allumettes_restantes, fichier_ordi="data_bot", nb_retire_precedent=1, coefficient_retirer=2): 
		""" On initialise les variables associées aux allumettes."""
		self.iteration_tour = 0 # le joueur concerné par le tour 
		self.nb_joueurs = nb_joueurs # la limite entre les joueurs et les ordis 
		self.iteration_max_tour = len(liste_participant) # la limite à ne pas dépasser (on revient à 0 après)
		self.liste_participant = liste_participant
		self.allumettes_depart = allumettes_restantes
		self.allumettes_restantes = allumettes_restantes
		self.fichier_ordi = fichier_ordi
		self.nb_retire_precedent = nb_retire_precedent
		self.coefficient_retirer = coefficient_retirer
		self.fin_de_partie = False 

	def gestionTour(self):
		""" Méthode qui permet de choisir à qui est le tour (quel joueur ou quel ordinateur)."""
		"""
		print("Itération tour: " + str(self.iteration_tour))
		print("Itération max: " + str(self.iteration_max_tour))
		print("Liste: " + str(self.liste_participant))
		"""
		if(self.iteration_tour == self.iteration_max_tour - 1 or self.iteration_tour == self.iteration_max_tour): # dernière itération avant de retourner au début de la liste
			if(self.iteration_tour == self.iteration_max_tour): # on élimine un joueur tout en passant au tour suivant : source d'erreur (itération trop grande)
				self.iteration_tour -= 1 
			if(self.iteration_tour < self.nb_joueurs): # pas "=" car 1 de décalage 
				self.tourJoueur()
			else: 
				self.tourOrdi()
			self.iteration_tour = 0
		else: # on joue normalement 
			if(self.iteration_tour < self.nb_joueurs):
				self.tourJoueur()
			else:
				self.tourOrdi()
			self.iteration_tour += 1 
		return None

	def tourJoueur(self):
		""" Méthode qui gère le tour du joueur."""
		# on obtient le nombre d'allumettes à retirer
		nb_a_retirer = 0 
		while(nb_a_retirer < 1 or nb_a_retirer > self.nb_retire_precedent * self.coefficient_retirer or nb_a_retirer > self.allumettes_restantes): 
			nb_a_retirer = int(input("Combien d'allumettes {} retire-t-il ({} maximum) ?".format(self.liste_participant[self.iteration_tour], min(self.nb_retire_precedent * self.coefficient_retirer, self.allumettes_restantes))))
		self.miseJourInfosTour(nb_a_retirer)
		# on teste si la partie est finie ou non  
		self.gestionFinPartie()
		return None

	def tourOrdi(self):
		""" Méthode qui gère le tour de l'ordinateur."""
		meilleure_proba = 0
		meilleur_nb_a_retirer = 1
		if(self.allumettes_restantes == 1): # le meilleur nb à retirer reste 1
			pass 
		else: 
			with open(self.fichier_ordi, "rb") as f: # on ouvre le fichier qui contient l'analyse des données
				tableau_stats = pickle.Unpickler(f).load()
				for i in range(1, self.nb_retire_precedent * self.coefficient_retirer): # on teste pour chaque combinaison le score le plus élevé
					combinaison = "{} - {}".format(self.allumettes_restantes, i) # combinaison de valeurs que l'on va chercher dans le tableau
					print(combinaison)
					if(combinaison in tableau_stats and tableau_stats[combinaison] > meilleure_proba): # la combinaison a une probabilité de victoire associée plus grande que la meilleure d'avant
						# print("La meilleure proba devient {} en retirant {} allumettes.".format(tableau_stats[combinaison], i))
						meilleur_nb_a_retirer = i 
						meilleure_proba = tableau_stats[combinaison]
					else: # le meilleur nb à retirer reste 1
						pass
				pourcent_partie_restant = self.allumettes_restantes / self.allumettes_depart 
				if(pourcent_partie_restant > 0.3 and meilleur_nb_a_retirer == 1): 
					palier_bas = math.ceil(pourcent_partie_restant * self.nb_retire_precedent * self.coefficient_retirer)
					meilleur_nb_a_retirer = random.randint(palier_bas, self.nb_retire_precedent * self.coefficient_retirer) # c'est pas drôle s'il joue 1 alors on lui fait jouer qqch de grand aléatoirement 
		nb_a_retirer = meilleur_nb_a_retirer
		self.miseJourInfosTour(nb_a_retirer)
		# on teste si la partie est finie ou non  
		self.gestionFinPartie()
		return None

	def miseJourInfosTour(self, nb_a_retirer):
		""" Méthode qui met à jour les informations à chaque tour et affiche un message de compte-rendu."""
		self.allumettes_restantes -= nb_a_retirer
		self.nb_retire_precedent = nb_a_retirer
		print("{} a retiré {} allumette(s), reste {}.".format(self.liste_participant[self.iteration_tour], self.nb_retire_precedent, self.allumettes_restantes))
		return None


class ModeClassique(Allumette):
	"""Le mode classique du jeu d'allumette : au premier "mort", la partie s'arrête."""
	def __init__(self, nb_joueurs, liste_participant, allumettes_restantes, fichier_ordi, nb_retire_precedent, coefficient_retirer): 
		# on reprend uniquement le constructeur d'Allumette
		Allumette.__init__(self, nb_joueurs, liste_participant, allumettes_restantes, fichier_ordi, nb_retire_precedent, coefficient_retirer)

	def gestionFinPartie(self): 
		""" Méthode qui permet de gérer la fin de la partie."""
		if(self.allumettes_restantes == 0): 
			self.fin_de_partie = True 
			print("Aye aye aye ... {}, tu as perdu.".format(self.liste_participant[self.iteration_tour]))
		else:
			self.fin_de_partie = False 
		return None


class ModeSurvivant(Allumette):
	""" Le mode dernier survivant du jeu d'allumette : le jeu s'arrête quand il n'y a plus qu'une personne en vie.
	À chaque personne éliminée, les allumettes et autres variables peuvent varier, ou non."""
	def __init__(self, nb_joueurs, liste_participant, allumettes_restantes, fichier_ordi, nb_retire_precedent, coefficient_retirer, evolution_allumettes_depart, evolution_coefficient_retirer, palier_pour_evolution):
		Allumette.__init__(self, nb_joueurs, liste_participant, allumettes_restantes, fichier_ordi, nb_retire_precedent, coefficient_retirer)
		self.nombre_participant = len(liste_participant)
		self.nombre_elimine = 0
		self.classement = []
		self.evolution_allumettes_depart = evolution_allumettes_depart
		self.evolution_coefficient_retirer = evolution_coefficient_retirer
		self.palier_pour_evolution = palier_pour_evolution

	def gestionFinPartie(self): 
		""" Méthode qui permet de gérer la fin de la partie et l'élimination d'un participant."""
		if(self.allumettes_restantes == 0):
			# on supprime le participant qui a perdu
			print("Aye aye aye ... {}, tu as perdu.".format(self.liste_participant[self.iteration_tour]))
			self.classement.append(self.liste_participant[self.iteration_tour]) # on ajoute le perdant au classement 
			self.nombre_participant -= 1 
			self.iteration_max_tour -= 1 
			del self.liste_participant[self.iteration_tour]
			if(self.iteration_tour < self.nb_joueurs): # le participant éliminé est un joueur 
				self.nb_joueurs -= 1

			# on met à jour les valeurs du jeu 
			self.nombre_elimine += 1
			if(self.nombre_elimine % self.palier_pour_evolution == 0): # on a atteint un palier 
				self.allumettes_depart += self.evolution_allumettes_depart
				self.coefficient_retirer += self.evolution_coefficient_retirer
			# on remet des allumettes pour que la partie continue 
			self.allumettes_restantes = self.allumettes_depart
			if(self.nombre_participant == 1): # s'il n'y a plus qu'un participant, il a gagné 
				# affichage du classement
				self.classement.append(self.liste_participant[0])
				self.classement.reverse() # on inverse les valeurs de la liste
				print("\n# ---- Voici le classement final : ---- #")
				for i in range(len(self.classement)):
					print("{} : {} !".format(i + 1, self.classement[i]))
				print("# ---- Merci d'avoir joué ---- #\n")
				self.fin_de_partie = True
		else:
			self.fin_de_partie = False 
		return None


class ModeMachineLearning(Allumette):
	"""Mode similaire au mode classique, seulement les ordinateurs jouent aléatoirement et on garde les logs."""
	def __init__(self, nb_joueurs, liste_participant, allumettes_restantes, fichier_ordi, nb_retire_precedent, coefficient_retirer): 
		# les logs permettent de stocker les coups joués par les ordis avant de les stocker dans le fichier
		Allumette.__init__(self, nb_joueurs, liste_participant, allumettes_restantes, fichier_ordi, nb_retire_precedent, coefficient_retirer)
		self.log_o1 = ""
		self.log_o2 = ""

	def tourOrdi(self):
		""" Méthode qui gère le tour de l'ordinateur. On joue de manière aléatoire."""
		allumettes_restantes_debut_tour = self.allumettes_restantes
		if(self.allumettes_restantes == 1):
			nb_a_retirer = 1
		else:
			nb_a_retirer = random.randint(1, min(self.allumettes_restantes, self.nb_retire_precedent * self.coefficient_retirer))
		self.miseJourInfosTour(nb_a_retirer)
		if(self.iteration_tour % 2 == 0):
			self.log_o1 += "{} - {} --> status\n".format(allumettes_restantes_debut_tour, nb_a_retirer)
		else: 
			self.log_o2 += "{} - {} --> status\n".format(allumettes_restantes_debut_tour, nb_a_retirer)
		# on teste si la partie est finie ou non  
		self.gestionFinPartie()

		return None

	def gestionFinPartie(self): 
		""" Méthode qui permet de gérer la fin de la partie."""
		if(self.allumettes_restantes == 0): 
			self.fin_de_partie = True 
			print("Aye aye aye ... {}, tu as perdu.".format(self.liste_participant[self.iteration_tour]))
			if(self.iteration_tour % 2 == 0):
				self.log_o1 = self.log_o1.replace("status", "D")
				self.log_o2 = self.log_o2.replace("status", "V")
			else:
				self.log_o1 = self.log_o1.replace("status", "V")
				self.log_o2 = self.log_o2.replace("status", "D")
		else:
			self.fin_de_partie = False 
		return None


def obtenirInfosClasse(): 
	""" Fonction qui permet d'obtenir les informations nécessaires à la création de la classe allumette : 
	nom du joueur, nb d'allumettes, nb retiré au premier tour, coefficient de "retirement" """
	# on récupère une liste de joueur(s) et d'ordi(s)
	nb_joueurs = 0 
	liste_participant = []
	while(nb_joueurs < 1): 
		nb_joueurs = int(input("Nombre de joueur(s): "))
	for i in range(nb_joueurs): 
		liste_participant.append(input("Nom du joueur n°{}: ".format(i + 1)))
	nombre_ordi = -1 
	while(nombre_ordi < 0): 
		nombre_ordi = int(input("Nombre d'ordinateur(s): "))
	for i in range(nombre_ordi):
		liste_participant.append("Ordinateur n°{}".format(i + 1))

	# les variables par défaut 
	allumettes_restantes = 30
	nb_retire_precedent = 1
	coefficient_retirer = 2
	if(input("Souhaitez-vous modifier les valeurs par défaut ?[o/n]\
		\n- allumettes : {}\
		\n- nb retiré au premier tour : {}\
		\n- coefficient de \"retirement\" : {}\n".format(allumettes_restantes, nb_retire_precedent, coefficient_retirer)).lower() == "o"): 
		allumettes_restantes = 0 
		while(allumettes_restantes < 1): 
			allumettes_restantes = int(input("Nombre d'allumettes au début de la partie: "))
		nb_retire_precedent = 0
		while(nb_retire_precedent < 1):
			nb_retire_precedent = int(input("Nombre d'allumettes retirées au premier tour: "))
		coefficient_retirer = 0 
		while(coefficient_retirer < 2): 
			coefficient_retirer = int(input("Coefficient de \"retirement\": "))
	return (nb_joueurs, liste_participant, allumettes_restantes, nb_retire_precedent, coefficient_retirer)


def obtenirInfosSupModeSurvivant():
	""" Fonction qui permet de récupérer en plus des informations nécessaires à la création de la classe allumette des informations optionnelles :
	diminution ou augmentation du nombre d'allumettes, du coefficient de retirement, en fonction du nombre de personnes éliminées."""
	evolution_allumettes_depart = 0
	evolution_coefficient_retirer = 0
	palier_pour_evolution = 1
	if(input("Souhaitez-vous modifier les valeurs par défaut ?[o/n]\
		\n- évolution du nombres d'allumettes au départ : {}\
		\n- évolution du coefficient de \"retirement\" : {}\
		\n- palier d'éliminés à atteindre pour chaque évolution : {}\n".format(evolution_allumettes_depart, evolution_coefficient_retirer, palier_pour_evolution)).lower() == "o"):
		evolution_allumettes_depart = int(input("Nombre d'allumettes à ajouter (valeur négative : retirer) tous les paliers: "))
		evolution_coefficient_retirer = int(input("Valeur à ajouter (ou retirer) au coefficient tous les paliers: "))
		l = 0 # l simule palier_pour_evolution que l'on doit laisser à 1 par défaut pour éviter un modulo par 0. Mais si l'on veut changer palier, il ne doit pas être = 0
		while(l == 0):
			palier_pour_evolution = int(input("Un palier correspond à combien d'éliminés (=/= 0) ? "))
			l = palier_pour_evolution
	return (evolution_allumettes_depart, evolution_coefficient_retirer, palier_pour_evolution)


def main():
	""" Fonction qui agence le programme."""
	sortir = False 
	fichier_ordi = "data_bot"
	while sortir != True:
		menu = int(input("Que faire ?\
			\n0 - Sortir\
			\n1 - Mode classique du jeu des allumettes\
			\n2 - Mode survivant du jeu des allumettes\
			\n3 - \"Machine learning\" récolte\
			\n4 - \"Machine learning\" analyse\
			\n")) 
		if(menu == 0): 
			sortir = True

		elif(menu == 1): 
			nb_joueurs, liste_participant, allumettes_restantes, nb_retire_precedent, coefficient_retirer = obtenirInfosClasse()
			jeu = ModeClassique(nb_joueurs, liste_participant, allumettes_restantes, fichier_ordi, nb_retire_precedent, coefficient_retirer)
			while(jeu.fin_de_partie != True):
				jeu.gestionTour()

		elif(menu == 2):
			nb_joueurs, liste_participant, allumettes_restantes, nb_retire_precedent, coefficient_retirer = obtenirInfosClasse()
			evolution_allumettes_depart, evolution_coefficient_retirer, palier_pour_evolution = obtenirInfosSupModeSurvivant()
			jeu = ModeSurvivant(nb_joueurs, liste_participant, allumettes_restantes, fichier_ordi, nb_retire_precedent, coefficient_retirer, evolution_allumettes_depart, evolution_coefficient_retirer, palier_pour_evolution)
			while(jeu.fin_de_partie != True):
				jeu.gestionTour()

		elif(menu == 3):
			nom_fichier = input("Nom du fichier où stocker les informations ?") + ".txt"
			recolteDonnees(nom_fichier)

		elif(menu == 4):
			nom_fichier_a_analyser = input("Nom du fichier où sont stockées les informations à analyser (sans extension)") + ".txt"
			nom_fichier_a_creer = input("Où stocker l'analyse du fichier précédent ? ")
			analyseDonnees(nom_fichier_a_analyser, nom_fichier_a_creer)

		else:
			print("Erreur lors du choix de l'action.")


if __name__ == "__main__": 
	main()