#Le but de ce programme est de proposer une interface permettant de jouer au morpion n,n,n, ainsi que d'étudier l'efficacité de certaines stratégies en fonction de la taille du jeu
#C'est à dire proposer une grille de N par N, où 2 joueurs doivent aligner n jetons, en jouant tour par tour
#Le programme propose aussi des bots à stratégies variables, pouvant servir d'adversaires mais étant surtout utilisés lors de batteries de test, où ils s'affrontent à répétition afin d'évaluer leur efficacité.

from random import randint
import numpy as np
import matplotlib.pyplot as plt
import time

#1/
#______________(convolution) utile pour le bot utilisant la convolution plus tard_______
def prodConv(a,b,normal):
    size = len(a)
    c=0
    for i in range(size):
      for j in range(size):
        c+= (a[i][j])*(b[size-i-1][size-j-1])
    return c/normal

def iterConv(sel,noyau):
  n = len(sel)
  normal = 0
  for i in noyau:
    for j in i:
      normal+=j
  if normal == 0:
    normal =1
  resultat = [[] for i in range(n)]
  for i in range(n):
    for j in range(n):
      case = [[] for a in range(3)]
      indice = 0
      for l in range(j-1,j+2):
        for k in range(i-1,i+2):
          if k<0: k +=1
          elif k >=n : k -=1
          if l<0: l +=1
          elif l >=n : l -=1
          case[indice].append(sel[l][k])
        indice += 1
      resultat[j].append(prodConv(case,noyau,normal))
  return resultat


'''noyau'''

gauss3 = [[1,2,1],
        [2,4,2],
        [1,2,1]]


#affichage matrices
def show(mat):
  for i in mat:
    print(i)
  print(' ')

#2/
#__________Classe Grille, simule une grille de morpion_____________________________________
class Grille:
  def __init__(self,n1):
    global n
    n = n1
    self.taille = n
    self.grille = []
    self.casesVides = []
    for j in range(n):
      ligne = []
      for i in range(n):
        ligne.append(0)
        self.casesVides.append((i,j))
      self.grille.append(ligne)

  def case(self,x,y):
    return self.grille[y][x]
    #/!\ pas utile pour changer la valeur de la case

  def marquerCase(self,x,y,ox):
    for i in range(len(self.casesVides)):
      if (x,y) == self.casesVides[i]:
        del self.casesVides[i]
        self.grille[y][x] = ox
        return self.victoire(x,y)
    print('case invalide')

  def tourJoueur(self,ox,joueur):
    #acquisition xy
    while True:
      x,y= self.acquisition(ox,joueur)
    #fin_______________________
      result = self.marquerCase(x,y,ox)
      if result != None:
        return result
      print('case invalide')
     #en cas de case invalide on réitère la requète (uniquement pourl'humain, les ia ne peuvent choisir que des cases vides)
 


  #vérifie si le coup joué en (x,y) est gagnant en vérifiant ligne, colonne et diagonales
  def victoire(self,x,y):
    flag = True
    ox = self.case(x,y)
    for i in range(n):
      if self.case(i,y) != ox:
        flag = False
        break
    if not flag:
      for i in range(n):
        if self.case(x,i) != ox:
          flag = False
          break
        flag = True
    if x == y and not flag :
      for i in range(n):
        if self.case(i,i) != ox:
          flag = False
          break
        flag = True
    if x == n-y-1 and not flag :
      for i in range(n):
        if self.case(i,n-i-1) != ox:
          flag = False
          break
        flag = True
    return flag,ox





  #fonction inutiles
  def copy(self):
    copie = Grille(n)
    copie.casesVides = self.casesVides
    for i in range(n):
      copie.grille[i] = self.grille[i]
    return copie

  def reset(self):
    self.casesVides = []
    for i in range(n):
      for j in range(n):
        self.grille[j][i]=0
        self.casesVides.append((j,i))
       
  def afficher(self):
    show(self.grille)





#3/  
  #____________________________________Joueurs_____________________________________________
  def acquisition(self,ox,joueur):
    if joueur == 'humain':
      x,y = self.humain(ox)
    elif joueur == 'iaRand':
      x,y = self.iaRand(ox)
    elif joueur == 'iaMalin':
      x,y = self.iaMalin(ox)
    elif joueur == 'iaRemplissage':
      x,y = self.iaRemplissage(ox)
    elif joueur == 'iaMilieuRectangle':
      x,y = self.iaMilieuRectangle(ox)
    elif joueur == 'iaCoinRectangle':
      x,y = self.iaCoinRectangle(ox)
    elif joueur == 'iaConvMax':
      x,y = self.iaConvMax(ox)
    elif joueur == 'iaConvMin':
      x,y = self.iaConvMin(ox)
    elif joueur == 'iaConvMoy':
      x,y = self.iaConvMoy(ox)
    return x,y

#3.1/
  #humain
  def humain(self,ox):
    print('Tour joueur',ox)
    self.afficher()
    print('case?')
    x,y = input()
    return int(x),int(y)

#3.2/
  #Random
  def iaRand(self,ox):
    if self.casesVides :
      n1 = len(self.casesVides)-1
      i = randint(0,n1)
      return self.casesVides[i]
#3.3/
  #Malin : random mais bouche toute case qui serait un coup gagnant pour J1 ou J2
  def malin(self):
    if self.casesVides :
      for i in range(n):
        c1,c2,c3,c4 = 0,0,0,0
        for j in range(n):
          c1 += self.case(i,j)
          c2 += self.case(j,i)
          c3 += self.case(j,j)
          c4 += self.case(j,n-1-j)
        if abs(c1) == (n-1):
          for k in self.casesVides:
            if k[0]==i:
              return k
        elif abs(c2) == (n-1):
          for k in self.casesVides:
            if k[1]==i:
              return k
        elif abs(c3) == (n-1):
          for k in self.casesVides:
            if k[0]==k[1]:
              return k
        elif abs(c4) == (n-1):
          for k in self.casesVides:
            if k[0]==n-1-k[1]:
              return k
      return -1,-1
 
  def iaMalin(self,ox):
    x,y = self.malin()
    if x == -1:
      return self.iaRand(ox)
    else:
      return x,y
   

#3.4/
  #Rectangles : se sert d'un algo rapide qui repère le plus grand rectangle vide
  #2 IAs : une se place au centre, l'autre dans un coin

#3.4.1/
    #Renvoie un tableau ou la case (i,j) contient la taille  de la colonne de zéros partant
    #de la case i,j du tableau
  def colonneZeros(self,tab,n):
    col = [n*[0] for i in range(n)]
    for i in range(n):
      if tab[0][i]==0 :
        col[0][i]=1
    for i in range(1,n):
      for j in range(n):
        if tab[i][j]==0:
          col[i][j]= 1+col[i-1][j]
        else:
          col[i][j]=0
    return col

#3.4.2/
    #renvoie une liste L où L[i] contient le premier indince k plus petit que i tel que
    #histo[i] > histo[k]
  def Lhisto(self,histo,n):
    L = [i for i in range(n)]
    for i in range(1,n):
      j=i
      while j>=0:
        if j==0:
          L[i]=0
          break
        else:
          if histo[j-1]<histo[i]:
            L[i]=j
            break
          else:
            j=L[j-1]
    return L

#3.4.3/
    #idem que Rhisto mais pour les indices plus grands que i:
    #renvoie une liste R où R[i] contient le premier indince k plus grand que i tel que
    #histo[i] > histo[k]
  def Rhisto(self,histo,n):
    R = [i for i in range(n)]
    for i in range(1,n):
      j=i
      while j<=(n-1):
        if j==(n-1):
          R[i]=n-1
          break
        else:
          if histo[j+1]<histo[i]:
            R[i]=j
            break
          else:
            j=R[j+1]
    return R

#3.4.4/
    #pGRH = plus Grand Rectangle histo : calcule le plus grand rectangle (en surface)
    #d'un histograme de tailles de colonnes
  def pGRH(self,histo,n):
    L = self.Lhisto(histo,n)
    R = self.Rhisto(histo,n)
    imax,smax = 0,0
    for i in range(n):
      s = (R[i]-L[i]+1)*(histo[i])
      if s > smax:
        smax = s
        imax = i
    return smax,L[imax],R[imax],histo[imax]

#3.4.5/
    #calcule le plus grand rectangle (en surface) d'un tableau
  def rectangleMax(self,tab,n):
    col = self.colonneZeros(tab,n)
    smax,Lmax,Rmax,hmax,jmax = 0,0,0,0,0
    for j in range(n):
      s,L,R,h = self.pGRH(col[j],n)
      if s > smax:
        smax = s
        Lmax = L
        Rmax = R
        hmax = h
        jmax = j
    return Lmax,Rmax,jmax,hmax

#3.4.6/
    #joue au milieu du rectangle
  def milieuRectangle(self):
    L,R,j,h = self.rectangleMax(self.grille,n)
    x = (L+R)//2
    y = (2*j - h +1)//2
    return x,y

    #joue dans un coin bas gauche du rectagnle, peu d'importance car le plateau
    #est symétrique
  def coinRectangle(self):
    L,R,j,h = self.rectangleMax(self.grille,n)
    return L,j

#3.4.7/
  def iaMilieuRectangle(self,ox):
    x,y = self.malin()
    if x == -1:
      return self.milieuRectangle()
    else:
      return x,y


  def iaCoinRectangle(self,ox):
    x,y = self.malin()
    if x == -1:
      return self.coinRectangle()
    else:
      return x,y

#3.5
  #convolution
  def nConv(self,noyau,n):
    a = self.grille
    for i in range(n):
      a = iterConv(a,noyau)
    return a
   
  #Stratégie : utiliser le flou par convolution
  #pour sentir aux alentours de quelle case l'adversaire est le plus présent, et le bloquer
  #problème : adversaire + présent n'implique pas forcément case la plus avantageuse
  def convMax(self,ox):
      matrice = self.nConv(gauss3, n) #convolution
      irep,jrep = -1,-1
      if ox == 1 :
          #J1 cherche la case de plus petit indice pour contrecarer J2
          imin,jmin = self.casesVides[0]
          min = matrice[jmin][imin]
          for k in range(1,len(self.casesVides)):
              i,j = self.casesVides[k]
              if matrice[j][i] < min:
                  min = matrice[j][i]
                  imin,jmin = i,j
          irep,jrep = imin,jmin
      elif ox == -1 :
          #J2 cherche la case de plus grand indice pour contrecarer J1
          imax,jmax = self.casesVides[0]
          max = matrice[jmiax][imax]
          for k in range(1,len(self.casesVides)):
              i,j = self.casesVides[k]
              if matrice[j][i] > max:
                  max = matrice[j][i]
                  imax,jmax = i,j
          irep,jrep = imax,jmax
      return irep,jrep

   

  #Stratégie : utiliser le flou par convolution
  #pour sentir aux alentours de quelle case l'adversaire est le moins présent, et s'y mettre
  def convMin(self,ox):
      matrice = self.nConv(gauss3, n) #convolution
      irep,jrep = -1,-1
      if ox == -1 :
          #J2 cherche la case de plus petit indice pour appuyer son avantage
          imin,jmin = self.casesVides[0]
          min = matrice[jmin][imin]
          for k in range(1,len(self.casesVides)):
              i,j = self.casesVides[k]
              if matrice[j][i] < min:
                  min = matrice[j][i]
                  imin,jmin = i,j
          irep,jrep = imin,jmin
      elif ox == 1 :
          #J1 cherche la case de plus grand indice pour appuyer son avantage
          imax,jmax = self.casesVides[0]
          max = matrice[jmax][imax]
          for k in range(1,len(self.casesVides)):
              i,j = self.casesVides[k]
              if matrice[j][i] > max:
                  max = matrice[j][i]
                  imax,jmax = i,j
          irep,jrep = imax,jmax
      return irep,jrep

  #Stratégie : utiliser le flou par convolution
  #pour repérer la case la moins proche des cases occupées et s'y placer
  def convMoy(self,ox):
      matrice = self.nConv(gauss3,n) #convolution
      #J1 ou J2 cherche la case d'indice le plus petit en valeur absolue :
      #c'est celui qui aura le plus d'impact
      imin,jmin = self.casesVides[0]
      min = abs(matrice[jmin][imin])
      for k in range(1,len(self.casesVides)):
        i,j = self.casesVides[k]
        if abs(matrice[j][i]) < min:
          min = matrice[j][i]
          imin,jmin = i,j
      return imin,jmin

  #les IAs
  def iaConvMax(self,ox):
    x,y = self.malin()
    if x == -1:
      return self.convMax(ox)
    else:
      return x,y

  def iaConvMin(self,ox):
    x,y = self.malin()
    if x == -1:
      return self.convMin(ox)
    else:
      return x,y

  def iaConvMoy(self,ox):
    x,y = self.malin()
    if x == -1:
      return self.convMoy(ox)
    else:
      return x,y

#4/
#partie classique, on marque une case en inscrivant ses coordonnées dans la console. Par exemple 00 marque la case en haut à gauche, 0n celle en bas à gauche, nn celle en bas à droite etc...

#4.1/
def jouer():
  print('taille du jeu?')
  n = int(input())
  tic = Grille(n)
  flag,gagnant = False,0
  print('joueur 1?')
  J1 = input()
  print('joueur 2?')
  J2 = input()
  while True:
    flag,gagnant=tic.tourJoueur(1,J1)
    if flag:
      break
    if tic.casesVides == []:
      print('Match Nul')
      tic.afficher()
      return ()
    flag,gagnant=tic.tourJoueur(-1,J2)
    if flag:
      break
    if tic.casesVides == []:
      print('Match Nul')
      tic.afficher()
      return ()
  print('gagnant: joueur',gagnant)
  tic.afficher()

#4.2/
#simule une partie de taille 'taille' entre 2 bots (J1 et J2), renvoie le numéro du joueur gagnant, et 0 en cas d'égalité
def simulation(J1,J2,taille):
  tic = Grille(taille)
  flag,gagnant = False,0
  #t1 = time.time()
  while True:
    flag,gagnant=tic.tourJoueur(1,J1)
    #tic.afficher()
    if flag:
      break
    if tic.casesVides == []:
      gagnant = 0
      break
    flag,gagnant=tic.tourJoueur(-1,J2)
    #tic.afficher()
    if flag:
      break
    if tic.casesVides == []:
      gagnant = 0
      break
  #t2 = time.time()
  #print(t2 - t1)
  tic.show()
  return gagnant


#4.3/
#simule 'iter' parties de taille 'taille' entre J1 et J2, et renvoie le nombre d'égalités v0, le nombre de victoires respectives de J1 et J2 v1 et v2, ainsi que la moyenne des scores, une victoire de J1 marquant +1 et une de J2 marquant -1
def test(J1,J2,taille,iter):
  v0,v1,v2,moy = 0,0,0,0
  for j in range(iter):
    resultat = simulation(J1,J2,taille)
    if resultat == 1:
      v1 += 1
    elif resultat == -1:
      v2 += 1
    moy += resultat
  v0 = iter - v1 - v2
  return v0,v1,v2,(moy/iter)


#4.4/
#teste J1 contre J2 'iter' fois sur des grilles de taille 1 à 'max', renvoie les listes des valeurs v0 v1 v2 et moy correspondant au test pour chaque taille de grille sous forme de liste, ainsi qu'une liste des tailles utilisées
def batterieTest(J1,J2,max,iter):
  #t1 = time.time()
  l0,l1,l2,lmoy = [],[],[],[]
  taille = []
  for i in range(1,max):
    v0,v1,v2,moy = test(J1,J2,i,iter)
    taille.append(i)
    l0.append(v0)
    l1.append(v1)
    l2.append(v2)
    lmoy.append(moy)
  #t2 = time.time()
  #print(t2 - t1)
  return l0,l1,l2,lmoy,taille


#4.5/
#affiche 3 graphes montrant respectivement le nombre de victoires de J1 (croix bleues) et de J2 (ronds rouges) ainsi que la moyenne des scores en fonction de la taille du jeu
def graphe(J1,J2,max,iter):
  t1 = time.time()
  l0,l1,l2,lmoy,taille = batterieTest(J1,J2,max,iter)
  t2 = time.time()
  fig1,ax1 = plt.subplots()
  fig2,ax2 = plt.subplots()
  figMoy,axMoy = plt.subplots()
  #tracé
  axMoy.plot(taille, lmoy,'g*' ,label='moyenne')
  ax1.plot(taille, l1,'bx' ,label='J1')
  ax2.plot(taille, l2,'ro' ,label='J2')
  #légende des axes
  axMoy.set_xlabel('taille')
  ax1.set_xlabel('taille')
  ax2.set_xlabel('taille')
  axMoy.set_ylabel('moyenne des scores')
  ax1.set_ylabel('victoires ' + J1)
  ax2.set_ylabel('victoires ' +J2)
  axMoy.legend()
  ax1.legend()
  ax2.legend()
  axMoy.set_title(J1+' vs '+J2)
  ax1.set_title(J1+' vs '+J2)
  ax2.set_title(J1+' vs '+J2)
  plt.show()
  print(t2-t1)
