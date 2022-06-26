import xml.etree.ElementTree as ET
from zipfile import ZipFile
import os
import shutil
import json

data = {} #variable retour

#-- Presque toutes les variables sont exprimées en unité/seconde pour ne pas dépendre de la durée du morceau, qui a déjà son propre indicateur --#

#tableau des notes (notation anglophone) en version full diez, full bemol, et normal
notesDiez = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']
notesBemol = ['C','Db','D','Eb','E','F','Gb','G','Ab','A','Bb','B']
notes = ['C','C#','D','Eb','E','F','F#','G','G#','A','Bb','B']
notesNoAlt = ['C','D','E','F','G','A','B']

ordre_alt = ['F','C','G','D','A','E','B']

# ✓ calcul du nombre de points en fonction des altérations (à la clé et dans le morceau) par seconde
# def pointsAlterations(nbCle, nbParMesure):
#     nbPointsCle = 12 #points par alteration à la clé
#     nbPointsNote = 15 #points par altération hors clé dans la musique
    
#     nbPoints = round(nbPointsCle*abs(nbCle) + nbPointsNote*nbParMesure)
#     print("Points alterations : " + str(nbPoints))
#     return nbPoints

#calcul du multiplicateur en fonction de la durée (en secondes)
# def multiplicateurDuree(duree): #nombre de minutes de la musique, jusqu'à *4
#     if(duree>240): duree = 240

#     nb = round(duree/60)
#     nb = 1 #TODO trouver une solution pour le multiplicateur
#     print("valeur du multiplicateur : " + str(nb))
#     return nb

# ✓ calcul du nombre de points en fonction du nombre de notes par seconde
def pointsNbNotesSec(nbNotesSec):
    nbPoints = 12 #nombre de points par note seconde
    if(nbNotesSec>=8):
        nbPoints = 25
    if(nbNotesSec>=14):
        nbPoints = 40

    nb = round(nbPoints*nbNotesSec)
    print("Points nombre de notes seconde : " + str(nb))
    return nb

# ✓ calcul du nombre de points en fonction du tempo
# def pointsTempo(tempo):
#     nb = round(math.exp(tempo*0.05))
#     # nb = round(tempo/3)
#     print("points tempo : " + str(nb))
#     return nb
    
# ✓ calcul du nombre de points en fonction du nombre de touches différentes utilisées
def pointsTouchesDiff(nbTouches):
    nbMultPointsParTouche = 3
    if(nbTouches>=24):
        nbMultPointsParTouche = 5
    if(nbTouches>=36):
        nbMultPointsParTouche = 7

    nb = nbTouches*nbMultPointsParTouche
    print("Points nombre de touches differentes : " + str(nb))
    return nb

# ✓ calcul du nombre de points en fonction des notes jouées (jumps, chords, ...)
def pointsNotes(tabDistNotes, nbMesure):
    points = 0
    for i in range(len(tabDistNotes)):
        if(tabDistNotes[i]<8):
            points+=8
        if(points>8):
            points+=12
        if(tabDistNotes[i] == 12):
            points+=10
        if(tabDistNotes[i]>12):
            points+=20
        if(points>24):
            points+=12+tabDistNotes[i]
        # points += tabDistNotes[i]*math.exp(tabDistNotes[i]*0.4) #TODO pas d'exponentiel c'est abusé

    nb = round(points/nbMesure)
    print("Points notes jouees distance entre note: " + str(nb))
    return nb

#calcul du nombre de points en fonction du time signature (1/1, 3/4, 4/4 "facile" sinon "dur")
# def pointsTimeSignature(num, den):
    # if(num==1 or den == 1): 
    #     print("Points time signature : 0")
    #     return 0
    # if((num==3 and den==4) or (num==3 and den == 3) or (num == 4 and den == 4)): 
    #     print("Points time signature : 15")
    #     return 15
    # print("Points time signature : 30")
    # return 30

#fonction de calcul de points total
def calcPoints(nbAlterationsCle, nb_alterations_mesure, nb_notes_secP1, nb_notes_secP2, tempo, nbNotesDifferentes, numerateur, denominateur, song_duration, tab_ecart_notesP1, tab_ecart_notesP2, nbMesures):
    score_final = 0
    # score_final += pointsAlterations(nbAlterationsCle, nb_alterations_mesure)
    score_final += pointsNbNotesSec(nb_notes_secP1)
    score_final += pointsNbNotesSec(nb_notes_secP2)
    # score_final += pointsTempo(tempo)
    score_final += pointsTouchesDiff(nbNotesDifferentes)
    # score_final += pointsTimeSignature(numerateur, denominateur)
    score_final += pointsNotes(tab_ecart_notesP1, nbMesures)
    score_final += pointsNotes(tab_ecart_notesP2, nbMesures)

    data[0] = {"pointsNotesSecondeP1" : pointsNbNotesSec(nb_notes_secP1), "pointsNotesSecondeP2" : pointsNbNotesSec(nb_notes_secP2), "pointsTouchesDiff" : pointsTouchesDiff(nbNotesDifferentes), "pointsEcartNotesP1" : pointsNotes(tab_ecart_notesP1, nbMesures), "pointsEcartNotesP2" : pointsNotes(tab_ecart_notesP2, nbMesures)}

    # score_final = score_final*multiplicateurDuree(song_duration)
    # print("total global : " + str(round(score_final)) + " pts")

#retourne le nombre de notes d'un tableau de notes (sans les silences)
def nombreNotes(array):
    nbNotes=0
    for i in range(len(array)):
        if(array[i] != ""): nbNotes+=1
    return nbNotes

#retourne le nombre de notes différentes jouées
def findNbUniqNote(array):
    tmp = []
    for i in range (len(array)):
        if(array[i] not in tmp):
            tmp.append(array[i])
    return len(tmp)

#calcul le nombre de demi-tons d'écart entre 2 notes
def ecartNote(n1, n2):
    octaveN1 = n1[len(n1)-1]
    octaveN2 = n2[len(n2)-1]
    nbOctaveDif = int(octaveN2) - int(octaveN1)
    indN1 = notes.index(n1.replace(octaveN1, ""))
    indN2 = notes.index(n2.replace(octaveN2, ""))

    nbDist = 0

    trouve = False

    #la note 1 est avant la note 2
    if(nbOctaveDif > 0):
        i=indN1
        while(not(trouve)):
            if(notes[i] == n2.replace(octaveN2, "")):
                trouve=True
            else: 
                nbDist+=1
            i+=1
            i=i%12
        
        if(indN1 <= indN2):
            return nbDist+abs(nbOctaveDif)*12
        return nbDist+abs(nbOctaveDif-1)*12

    #la note 2 est avant la note 1
    if(nbOctaveDif < 0):
        i=indN2
        nbDist=0
        while(not(trouve)):
            if(notes[i] == n1.replace(octaveN1, "")):
                trouve=True
            else: 
                nbDist+=1
            i+=1
            i=i%12

        if(indN2 <= indN1):
            return nbDist+(abs(nbOctaveDif))*12
        return nbDist+abs(nbOctaveDif+1)*12

    #les deux notes ont la même octave
    if(nbOctaveDif == 0):
        if(indN1 < indN2): #si la note 1 est avant la note 2 (sans octave)
            i=indN1
            while(not(trouve)):
                if(notes[i] == n2.replace(octaveN2, "")):
                    trouve=True
                else: 
                    nbDist+=1
                i+=1

        if(indN2 < indN1): #si la note 2 est avant la note 1 (sans octave)
            i=indN2
            nbDist=0
            while(not(trouve)):
                if(notes[i] == n1.replace(octaveN1, "")):
                    trouve=True
                else: 
                    nbDist+=1
                i+=1

        return nbDist

#nombre d'altérations "non prévues" par l'armature
def nbAlterationsNonCle(nbAltCle, array): #nbAltCle négatif si bemol, positif si diez
    notes_alt = []
    notes_autorise = notesNoAlt.copy()
    nbAlt = 0

    #cas des diez
    if(nbAltCle > 0):
        for i in range(nbAltCle): #ajout des notes altérées
            notes_alt.append(ordre_alt[i]+"#")
    
    #cas des bémols
    if(nbAltCle < 0):
        for i in range(abs(nbAltCle)):
            notes_alt.append(ordre_alt[len(ordre_alt) -1 -i]+"b")

    for i in range(len(notes_alt)): #replacement des notes "normales" par leur altération pour obtenir le tableau des notes de la gamme utilisée
            index = notes_autorise.index(notes_alt[i][0]) #index de la note à replacer
            notes_autorise[index] = notes_alt[i]

    for i in range(len(array)):
        if(array[i] != "" and array[i][:-1] not in notes_autorise and array[i][:-1] not in notesNoAlt): # [:-1] -> ne pas tenir compte du chiffre de l'octave
            nbAlt+=1
    
    return nbAlt
    
#
def rangeTab(array):
    finalTab = []
    for i in range(len(array)):
        newNote = array[i]
        if(len(array[i]) == 3):
            note = array[i][0]
            alt = array[i][1]
            oct = array[i][2]
            if(alt == "#"):
                newNote = notes[(notes.index(note)+1)%12] + oct
            if (alt == "b"):
                newNote = notes[(notes.index(note)-1+12)%12] + oct
        finalTab.append(newNote)

    return finalTab

#calcule les écart de notes pour un tableau donné
def ecartNotes(array):
    finalTab = []
    for i in range(len(array)-1):
        j=i
        note1 = array[i]
        note2 = array[i+1]

        if(note2 == ""): #si silence, on a le temps de se déplacer, aucun écart
            #TODO changer ça ? ou je laisse ?
            finalTab.append(0)
        else:
            if(note1 != ""):
                finalTab.append(ecartNote(note1,note2))
    
    return finalTab

#moyenne des écarts de notes pour chaque mesure
def ecartNotesMesure(array1, array2):
    #array1 = écarts des notes d'une portée
    #array2 = nombre de notes d'une mesure
    final_tab = []
    nb_parcourus = 0 #ñombre de notes déjà passées
    for i in range(len(array2)):
        somme = 0
        for j in range(array2[i]):
            somme += array1[j+nb_parcourus]
        somme = round(somme / array2[i])
        final_tab.append(somme)
        nb_parcourus += array2[i]-1

    return final_tab

#trouver les break points de difficulté, par vitesse et par jump
def findBreak(arrayP1, arrayP2, array3, array4, nbMesuresTot):
    #arrayP1 et arrayP2 sont les tableaux de notes/s pour portée 1 et portée 2
    #array3 et array4 sont les tableaux de l'écart des notes pour les portées 1 et 2 
    toleranceVitesse = 0.5
    toleranceJump = 3
    toleranceNbMesures = 1.3
    final_tab = [] #tableau de tous les break points
    final_tab1Speed = [] #tableau de tous les break points
    final_tab2Speed = []
    final_tab1Jump = []
    final_tab2Jump = []

    for i in range(len(arrayP1)-1):
        if(arrayP1[i+1]>arrayP1[i]*(1+toleranceVitesse) or arrayP1[i+1]<arrayP1[i]*toleranceVitesse):
            final_tab1Speed.append(i)
        if(arrayP2[i+1]>arrayP2[i]*(1+toleranceVitesse) or arrayP2[i+1]<arrayP2[i]*toleranceVitesse):
            final_tab2Speed.append(i)
                
    for i in range(len(array3)-1): #TODO y a certainement des choses à revoir ici
        if(array3[i+1]>array3[i]*(1+toleranceJump) or array3[i+1]<array3[i]*toleranceJump):
            final_tab1Jump.append(i)
        if(array4[i+1]>array4[i]*(toleranceJump) or array4[i+1]<array4[i]*toleranceJump):
            final_tab2Jump.append(i)
    
    for i in range (len(final_tab1Speed)):
        if((final_tab1Speed[i] in final_tab2Speed) and (final_tab1Speed[i] in final_tab1Jump) and (final_tab1Speed[i] in final_tab2Jump) and (final_tab1Speed[i] != 0)):
            final_tab.append(final_tab1Speed[i])


    final_tab.sort()
    tmp = []

    for i in range(len(final_tab)-1):
        if(not(final_tab[i]+toleranceNbMesures>final_tab[i+1])):
            tmp.append(final_tab[i])
    tmp.append(final_tab[len(final_tab)-1]) #ajouter le dernier élément du tableau qui ne peut pas être comparé

    if(not(nbMesuresTot) in tmp):
        tmp.append(nbMesuresTot)

    return tmp

def calcPointsSection(nb_notes_secP1, nb_notes_secP2, tab_ecart_notesP1, tab_ecart_notesP2, nbMesures, numSection, dureeSection, mesureStart, mesureEnd, tempo):
    score_final = 0
    # score_final += pointsTempo(tempo)
    score_final += pointsNbNotesSec(nb_notes_secP1)
    score_final += pointsNbNotesSec(nb_notes_secP2)
    if(nbMesures > 0):
        score_final += pointsNotes(tab_ecart_notesP1, nbMesures)
        score_final += pointsNotes(tab_ecart_notesP2, nbMesures)

    print("total section " + str(numSection) +" : " + str(round(score_final)) + " pts")
    print("duree totale de la section : " + str(round(dureeSection)) + "s | Section de la mesure " + str(mesureStart+1) + " a " + str(mesureEnd+1))
    print("------------")

    data[numSection] = {"pointsNotesSecondeP1" : pointsNbNotesSec(nb_notes_secP1), "pointsNotesSecondeP2" : pointsNbNotesSec(nb_notes_secP2), "pointsEcartNotesP1" : pointsNotes(tab_ecart_notesP1, nbMesures), "pointsEcartNotesP2" : pointsNotes(tab_ecart_notesP2, nbMesures), "scoreSection" : round(score_final), "dureeSection" : round(dureeSection), "mesureStart" : mesureStart+1, "mesureEnd" : mesureEnd+1}
    return score_final

def calcSection(tab_break_measures, tab_ecart_notes_mesureP1, tab_ecart_notes_mesureP2, tabNoteP1, tabNoteP2, measure_duration, tab_mesures_nb_notesP1, tab_mesures_nb_notesP2, tempo):
    tab_score_section = []
    tab_duree_section = []
    nbMesuresParcourues = 0
    for i in range(len(tab_break_measures)): #pour chaque section
        tab_ecart_notes_mesureP1_section = []
        tab_ecart_notes_mesureP2_section = []
        nbNotesP1 = 0
        nbNotesP2 = 0
        nbNotesSecP1 = 0
        nbNotesSecP2 = 0
        for j in range(nbMesuresParcourues, tab_break_measures[i]):
            tab_ecart_notes_mesureP1_section.append(tab_ecart_notes_mesureP1[j])
            tab_ecart_notes_mesureP2_section.append(tab_ecart_notes_mesureP2[j])

        for j in range(nbMesuresParcourues, tab_break_measures[i]):
            nbNotesP1+=tab_mesures_nb_notesP1[j]
            nbNotesP2+=tab_mesures_nb_notesP2[j]

        dureeSection = (measure_duration*(tab_break_measures[i]-nbMesuresParcourues))
        if(dureeSection != 0):
            nbNotesSecP1 = round(nbNotesP1/dureeSection)
            nbNotesSecP2 = round(nbNotesP2/dureeSection)
        
        nbMesuresSection = tab_break_measures[i]-nbMesuresParcourues
        tab_score_section.append(calcPointsSection(nbNotesSecP1, nbNotesSecP2, tab_ecart_notes_mesureP1_section, tab_ecart_notes_mesureP2_section, nbMesuresSection, i+1, dureeSection, nbMesuresParcourues, tab_break_measures[i], tempo))
        tab_duree_section.append(dureeSection)
        nbMesuresParcourues=tab_break_measures[i]
    
    # print(tab_score_section)
    moyenneSections = 0
    for i in range(len(tab_score_section)):
        moyenneSections+=tab_score_section[i]*tab_duree_section[i]
    
    moyenneSections = round(moyenneSections/sum(tab_duree_section))
    print("Difficulte moyenne "+str(moyenneSections)+" pts")

#fonction principale du calcul de difficulté d'un fichier
def main(file_name, name):
    #le parsing
    tree = ET.parse(file_name)
    root = tree.getroot()

    #les variables
    titre = name.split(".", 1)[0]
    # titre = root.find(".//work-title").text #TODO visiblement le chemin vers le titre n'est pas toujours le même
    nbAlterationsCle = int(root.find(".//fifths").text) #négatif si bémol, positif si diez
    nbMesures = 0
    nbNotes = 0
    tabNotes = []
    tabNoteP1 = [] #tableau de notes de la première portée
    tabNoteP2 = [] #tableau de notes de la seconde portée

    numerateur = int(root.find(".//beats").text)
    denominateur = int(root.find(".//beat-type").text)
    # tempo = int(root.find(".//per-minute").text)
    # print(len(root.findall(".//per-minute")))
    sumTempo = 0
    for i in range(len(root.findall(".//per-minute"))):
        sumTempo+=int(root.findall(".//per-minute")[i].text)
    
    tempo = round(sumTempo/len(root.findall(".//per-minute")))

    nb_alterations_mesure = 0 #nombre moyen d'altérations hors armature par mesure
    nbNotesDifferentes = 0

    song_duration = 0
    nb_notes_sec = 0
    measure_duration = (numerateur/denominateur) * 4 * (60/tempo)

    tab_mesures_nb_notesP1 = [] #tableau de nombre de notes par mesure
    tab_mesures_nb_notesP2 = [] #tableau de nombre de notes par mesure
    tab_ecart_notesP1 = [] #tableau des écarts entre deux notes consécutives
    tab_ecart_notesP2 = [] 
    tab_ecart_notes_mesureP1 = [] #tableau des écarts entre deux notes consécutives pour une mesure
    tab_ecart_notes_mesureP2 = []

    tab_break_measures = [] #tableau qui liste toutes les mesures ou il y a des "cassures" dans la difficulté


    #recherche toutes les mesures dans l'arbre et remplir les tableaux
    for measure in root.findall(".//measure"):
        nbNoteMesureP1 = 0
        nbNoteMesureP2 = 0
        nbMesures += 1
        for note in measure.findall(".//note"): #parcourir chaque note

            n = "" #initialisé à chaine vide pour le cas des silences
            for pitch in note.findall(".//step"): #parcours des notes
                n = pitch.text
                if(note.find(".//alter") != None):
                    if(int(measure.find(".//alter").text) == 1): n += "#"
                    if(int(measure.find(".//alter").text) == -1): n += "b"
                
            for octave in note.findall(".//octave"): #les octaves
                n = n + octave.text

            tabNotes.append(n)

            #ajouter les notes à leur tableau respectifs selon leur portée
            if(int(note.find("staff").text) == 1):
                if(note != ""):
                    nbNoteMesureP1 += 1
                tabNoteP1.append(n)
            if(int(note.find("staff").text) == 2):
                if(note != ""):
                    nbNoteMesureP2 += 1
                tabNoteP2.append(n)

            #ne pas compter les silences dans le nombre total de notes
              
        tab_mesures_nb_notesP1.append(nbNoteMesureP1)
        tab_mesures_nb_notesP2.append(nbNoteMesureP2)

    nbNotes = nombreNotes(tabNotes)
    song_duration = (numerateur/denominateur) * 4 * nbMesures * (60/tempo)
    nb_notes_sec = nbNotes/song_duration
    nbNotesDifferentes = findNbUniqNote(tabNotes)
    nb_alterations_mesure = nbAlterationsNonCle(nbAlterationsCle, tabNotes) / nbMesures

    #remplacer les altérations non standardes par leur équivalent
    tabNoteP1 = rangeTab(tabNoteP1)
    tabNoteP2 = rangeTab(tabNoteP2)
    tabNotes = rangeTab(tabNotes)

    nb_notes_secP1 = len(tabNoteP1)/song_duration
    nb_notes_secP2 = len(tabNoteP2)/song_duration

    tab_ecart_notesP1 = ecartNotes(tabNoteP1)
    tab_ecart_notesP2 = ecartNotes(tabNoteP2)

    tab_ecart_notes_mesureP1 = ecartNotesMesure(tab_ecart_notesP1, tab_mesures_nb_notesP1)
    tab_ecart_notes_mesureP2 = ecartNotesMesure(tab_ecart_notesP2, tab_mesures_nb_notesP2)

    tab_break_measures = findBreak(tab_mesures_nb_notesP1, tab_mesures_nb_notesP2, tab_ecart_notes_mesureP1, tab_ecart_notes_mesureP2, nbMesures)

    print("---"+titre+"---\n")
    calcPoints(nbAlterationsCle, nb_alterations_mesure, nb_notes_secP1, nb_notes_secP2, tempo, nbNotesDifferentes, numerateur, denominateur, song_duration, tab_ecart_notesP1, tab_ecart_notesP2, nbMesures)
    print("\nScore par section\n")
    calcSection(tab_break_measures, tab_ecart_notes_mesureP1, tab_ecart_notes_mesureP2, tabNoteP1, tabNoteP2, measure_duration, tab_mesures_nb_notesP1, tab_mesures_nb_notesP2, tempo)
    print("\n||||||||||||||||||||||||||||||||||||||||||||||||||||||||\n")

#prend un objet mxl en paramètre et fait l'appel à main pour le programme principal
def mxlConvert(file):
    with ZipFile(file, 'r') as zipObj:
        listOfiles = zipObj.namelist()
        # Extract all the contents of zip file in current directory
        zipObj.extractall()

    for i in range(len(listOfiles)): #regarde les fichiers xml à la racine de l'archive
        if ".xml" in listOfiles[i] and not "/" in listOfiles[i]:
            main(listOfiles[i], file) #appel de la fonction principale
            #suppression des fichiers et dossiers inutiles après utilisation
            os.remove(listOfiles[i])
            shutil.rmtree('META-INF')
            #enregistrement des données dans un fichier json
            with open(file.split(".", 1)[0]+".json", 'w') as file: 
                json.dump( data, file )
    
    return data

mxlConvert("totoro.mxl")
mxlConvert("totoro2.mxl")
mxlConvert("days.mxl")