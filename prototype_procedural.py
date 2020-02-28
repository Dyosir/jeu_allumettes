# coding: utf-8 

# POUVOIR JOUER A PLUSIEURS JOUEURS 


def gestionFinPartie(allumettes_restantes, joueur): 
	""" Fonction qui vérifie si la partie est finie ou non."""
	if(allumettes_restantes == 0): 
		fin_de_partie = True
		print("Aye aye aye ... {}, tu as perdu.".format(joueur))
	else:
		fin_de_partie = False 
	return fin_de_partie


def tourJoueur(allumettes_restantes, nb_retire_precedent, coefficient_retirer, nom_joueur):
	""" Fonction qui gère le tour d'un joueur."""
	print("Il reste {} allumettes ({} retirée(s) au tour précédent).".format(allumettes_restantes, nb_retire_precedent))

	nb_a_retirer = 0 
	while(nb_a_retirer < 1 or nb_a_retirer > nb_retire_precedent * coefficient_retirer or nb_a_retirer > allumettes_restantes): 
		nb_a_retirer = int(input("Combien souhaitez-vous en retirer ? ({} maximum)".format(min(nb_retire_precedent * coefficient_retirer, allumettes_restantes))))

	# on met à jour les différents variables 
	allumettes_restantes -= nb_a_retirer
	nb_retire_precedent = nb_a_retirer
	print("Vous avez retiré {} allumette(s), reste {}.".format(nb_retire_precedent, allumettes_restantes))
	# et on teste si le partie est finie ou non 
	fin_de_partie = gestionFinPartie(allumettes_restantes, nom_joueur)
	return (allumettes_restantes, nb_retire_precedent, fin_de_partie)


def tourOrdi(allumettes_restantes, nb_retire_precedent, coefficient_retirer): 
	""" Fonction qui gère le tour de l'ordinateur."""
	if(allumettes_restantes - 1 <= nb_retire_precedent * coefficient_retirer): 
		nb_a_retirer = allumettes_restantes - 1
	else: 
		nb_a_retirer = max(1, min(nb_retire_precedent * coefficient_retirer, allumettes_restantes - (coefficient_retirer * (nb_retire_precedent * coefficient_retirer + 1))))
	# on met à jour les différentes variables 
	allumettes_restantes -= nb_a_retirer
	nb_retire_precedent = nb_a_retirer
	print("L'ordinateur a retiré {} allumette(s), reste {}.".format(nb_retire_precedent, allumettes_restantes))
	# et on teste si le partie est finie ou non 
	fin_de_partie = gestionFinPartie(allumettes_restantes, "Ordinateur")
	return (allumettes_restantes, nb_retire_precedent, fin_de_partie) 


def main():
	""" Fonction qui agence le programme."""
	nom_joueur = input("Nom du joueur: ")
	sortir = False 

	while sortir != True: 
		if(input("Continuer à jouer ? [o/n]").lower() == "n"): 
			sortir = True
		else:
			# les variables du début de partie 
			allumettes_restantes = 30
			nb_retire_precedent = 1
			coefficient_retirer = 2
			fin_de_partie = False
			if(input("Souhaitez-vous modifier les valeurs par défaut ?[o/n]\
				\n- allumettes : {} ;\
				\n- nb retiré au premier tour : {};\
				\n- coefficient de \"retirement\" : {};".format(allumettes_restantes, nb_retire_precedent, coefficient_retirer)).lower() == "o"): 
				allumettes_restantes = int(input("Allumettes: "))
				nb_retire_precedent = int(input("Nb retiré au premier tour: "))
				coefficient_retirer = int(input("Coefficient de \"retirement\": "))

			while(fin_de_partie != True):
				# tour du joueur 
				allumettes_restantes, nb_retire_precedent, fin_de_partie = tourJoueur(allumettes_restantes, nb_retire_precedent, coefficient_retirer, nom_joueur)
				if(fin_de_partie == True):
					pass
				else: 
					# tour de l'ordinateur 
					allumettes_restantes, nb_retire_precedent, fin_de_partie = tourOrdi(allumettes_restantes, nb_retire_precedent, coefficient_retirer) 


if __name__ == "__main__": 
	main()