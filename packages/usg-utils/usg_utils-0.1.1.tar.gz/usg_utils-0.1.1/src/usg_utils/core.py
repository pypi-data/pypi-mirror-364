import numpy as np
# from numpy import genfromtxt
import flopy.utils.binaryfile as bf   #Module to read MODFLOW binary output files
from pandas.core.common import flatten

#Function to know the length of the lpf file
def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
        return i+1
    
def read_gsf_file(root_name):
    file = open(root_name+'.gsf','r') #open gsf file
    gsf_data = file.readlines()
    return gsf_data

def getNumberOfNodes(root_name):
    gsf_data = read_gsf_file(root_name) #read gsf file
    nn = int((gsf_data[1]).split()[0]) #number of nodes
    return nn

def getNumberOfVertexes(root_name):
    gsf_data = read_gsf_file(root_name)
    nv = int(gsf_data[2]) #number of vertexs
    return nv

def getNumberOfLayers(root_name):
    gsf_data = read_gsf_file(root_name)
    nl = int((gsf_data[1]).split()[1]) #number of nodes
    return nl       

def getNumberOfNodesPerLayer(root_name):
    #En desarrollo
    nn = getNumberOfNodes(root_name)
    nl = getNumberOfLayers(root_name)
    npl = int(nn/nl)
    return npl
    
def getIbound(root_name):
    bas = root_name+'.bas'
    bas_file = open(bas,'r') #open bas file
    data3 = bas_file.readlines() #read bas file            
    
    nl = getNumberOfLayers(root_name)
    nn = getNumberOfNodes(root_name)
    npl = getNumberOfNodesPerLayer(root_name)
    
    lbas = file_len(bas) #Length of the lpf file
    count_ibound = np.zeros((1,nl)) #counter to save the line number with information for ibound
    ibound = np.zeros((nn,1)) #vector with property ibound
    remainder = int(npl%10)
    
    #Find line number with ibound Layer xxx and save in count_ibound
    for k in range(1,nl + 1):
        prop = 'IBOUND Layer ' + str(k)
        for j in range (1,lbas):
            aux = data3[j] #read every line
            if prop in aux:
                count_ibound[0,k-1] = j
                break
            
    #Assignate property to every node      
    for m in range(1,nl + 1):
        aux_2 = data3[int(count_ibound[0,m-1])]
        aux_3 = int(npl*(m-1))
        if aux_2.split()[0] == 'INTERNAL':
            for n in range(1,int(npl/10) + 1):
                ibound[10*(n-1) + aux_3 : 10*n + aux_3,0] = data3[int(count_ibound[0,m-1]) + n].split()
            if remainder == 0:
                ibound = ibound
            else:
                ibound[10*n + aux_3 : 10*n+remainder + aux_3,0] = data3[int(count_ibound[0,m-1]) + n + 1].split() #last line
        else: #for CONSTANT case
            for n in range(1,int(npl/10) + 1):
                ibound[10*(n-1) + aux_3 : 10*n + aux_3,0] = data3[int(count_ibound[0,m-1])].split()[1]
            if remainder == 0:
                ibound = ibound
            else:
                ibound[10*n + aux_3 : 10*n+remainder + aux_3,0] = data3[int(count_ibound[0,m-1]) + n + 1].split()[1] #last line
    
    ibound = np.reshape(ibound, len(ibound))
    return ibound

def getNodeCoords(root_name):
    gsf = root_name + '.gsf'
    nv = getNumberOfVertexes(root_name)
    nn = getNumberOfNodes(root_name)
    #Read coordinates of nodes
    G = np.loadtxt(gsf, skiprows = nv + 3) #skip vertex information
    coordinates = np.zeros((nn,4)) #node number, x, y, z
    coordinates[:,0] = G[:,0] #node
    coordinates[:,1] = G[:,1] #x
    coordinates[:,2] = G[:,2] #y
    coordinates[:,3] = G[:,3] #z
    
    return coordinates

def getVertexCoords(root_name):
    gsf = root_name + '.gsf'
    #Read coordinates of nodes
    nv = getNumberOfVertexes(root_name)
    V = np.loadtxt(gsf, skiprows = 3, usecols = (0,1,2)) #Read the 3 first columns of grid file
    Vertex = V[0:nv,:] #cut node information
    X = Vertex[:,0] #x
    Y = Vertex[:,1] #y
    Z = Vertex[:,2] #z
    
    return X.copy(),Y.copy(),Z.copy()  

def getNodeConnectivity(root_name):
    gsf = root_name + '.gsf'
    nv = getNumberOfVertexes(root_name)
    nn = getNumberOfNodes(root_name)
    G = np.loadtxt(gsf, skiprows = nv + 3) #skip vertex information
    conect = G[:,6:14]
    connectivity = np.reshape(conect,(8*nn)) - 1
    
    return connectivity

def getKx(root_name):
    lpf = str(root_name) + '.lpf'
    lpf_file = open(lpf,'r') #open lpf file
    data2 = lpf_file.readlines() #read lpf file
    nl = getNumberOfLayers(root_name) #gets number of layers
    nn = getNumberOfNodes(root_name) #gets number of nodes
    npl = getNumberOfNodesPerLayer(root_name) #number of nodes per layer
    
    llpf = file_len(lpf) #Length of the lpf file
    count_kx = np.zeros((1,nl)) #counter to save the line number with information for kx
    kx = np.zeros((nn,1)) #vector with property kx
    # remainder = int(npl%10) #Number of elements in the last line of every property. 10 is because lpf file orders in rows of 10 elements
    
    count_kx = []
    kx_data = []

    for k in range(1,nl + 1):
        prop = 'Kx Layer ' + str(k)
        for j in range (1,llpf):
            aux = data2[j] #read every line
            if prop in aux:
                count_kx.append(j)
                break
    
    # Assigns property to every node      
    for m in range(0,nl):
        aux_2 = data2[int(count_kx[m])]
        aux_3 = data2[count_kx[m]+1:(count_kx[m]+int(np.ceil(npl/10))+1)]
        
        if aux_2.split()[0] == 'INTERNAL':
            for n in range(0,int(np.ceil(npl/10))):
                kx_data.append(aux_3[n].split())    
                
        elif aux_2.split()[0] == 'CONSTANT':
            l = [float(aux_2.split()[1])] * npl
            kx_data.append(l)    
       
        elif aux_2.split()[0] == 'OPEN/CLOSE':
            kx_=root_name+str(m+1)+'._kx'
            kx_file = open(kx_,'r')
            kx_data.append(kx_file.readlines())
            
        else:
            print("unknown format of lpf file")
    
    kx = list(flatten(kx_data))
    kx = np.asarray(kx).astype(float)              
    return kx

def getKz(root_name):
    lpf = str(root_name) + '.lpf'
    lpf_file = open(lpf,'r') #open lpf file
    data2 = lpf_file.readlines() #read lpf file
    nl = getNumberOfLayers(root_name) #gets number of layers
    nn = getNumberOfNodes(root_name) #gets number of nodes
    npl = getNumberOfNodesPerLayer(root_name) #number of nodes per layer
    
    llpf = file_len(lpf) #Length of the lpf file
    count_kz = np.zeros((1,nl)) #counter to save the line number with information for kx
    kz = np.zeros((nn,1)) #vector with property kx
    # remainder = int(npl%10) #Number of elements in the last line of every property. 10 is because lpf file orders in rows of 10 elements
    
    count_kz = []
    kz_data = []

    for k in range(1,nl + 1):
        prop = 'Kz Layer ' + str(k)
        for j in range (1,llpf):
            aux = data2[j] #read every line
            if prop in aux:
                count_kz.append(j)
                break
    
    # Assigns property to every node      
    for m in range(0,nl):
        aux_2 = data2[int(count_kz[m])]
        aux_3 = data2[count_kz[m]+1:(count_kz[m]+int(np.ceil(npl/10))+1)]
        
        if aux_2.split()[0] == 'INTERNAL':
            for n in range(0,int(np.ceil(npl/10))):
                kz_data.append(aux_3[n].split())    
                
        elif aux_2.split()[0] == 'CONSTANT':
            l = [float(aux_2.split()[1])] * npl
            kz_data.append(l)    
       
        elif aux_2.split()[0] == 'OPEN/CLOSE':
            kz_=root_name+str(m+1)+'._kz'
            kz_file = open(kz_,'r')
            kz_data.append(kz_file.readlines())
            
        else:
            print("unknown format of lpf file")
    
    kz = list(flatten(kz_data))
    kz = np.asarray(kz).astype(float)              
    return kz

def getSy(root_name):
    
    lpf = str(root_name) + '.lpf'
    lpf_file = open(lpf,'r') #open lpf file
    data2 = lpf_file.readlines() #read lpf file
    nl = getNumberOfLayers(root_name) #gets number of layers
    nn = getNumberOfNodes(root_name) #gets number of nodes
    npl = getNumberOfNodesPerLayer(root_name) #number of nodes per layer
    
    llpf = file_len(lpf) #Length of the lpf file
    count_Sy = np.zeros((1,nl)) #counter to save the line number with information for Sy
    Sy = np.zeros((nn,1)) #vector with property Sy
#    remainder = int(npl%10) #Number of elements in the last line of every property. 10 is because lpf file orders in rows of 10 elements
    
    count_Sy = []
    Sy_data = []

    for k in range(1,nl + 1):
        prop = 'Sy Layer ' + str(k)
        for j in range (1,llpf):
            aux = data2[j] #read every line
            if prop in aux:
                count_Sy.append(j)
                break
        
    # Assigns property to every node      
    for m in range(0,nl):
        aux_2 = data2[int(count_Sy[m])]
        aux_3 = data2[count_Sy[m]+1:(count_Sy[m]+int(np.ceil(npl/10))+1)]
        
        if aux_2.split()[0] == 'INTERNAL':
            for n in range(0,int(np.ceil(npl/10))):
                Sy_data.append(aux_3[n].split())    
                
        elif aux_2.split()[0] == 'CONSTANT':
            l = [float(aux_2.split()[1])] * npl
            Sy_data.append(l)    
       
        elif aux_2.split()[0] == 'OPEN/CLOSE':
            Sy_=root_name+str(m+1)+'._S2'
            Sy_file = open(Sy_,'r')
            Sy_data.append(Sy_file.readlines())
            
        else:
            print("unknown format of lpf file")
    
    Sy = list(flatten(Sy_data))
    Sy = np.asarray(Sy).astype(float)                 
    return Sy

def getSs(root_name):
    lpf = str(root_name) + '.lpf'
    lpf_file = open(lpf,'r') #open lpf file
    data2 = lpf_file.readlines() #read lpf file
    nl = getNumberOfLayers(root_name) #gets number of layers
    nn = getNumberOfNodes(root_name) #gets number of nodes
    npl = getNumberOfNodesPerLayer(root_name) #number of nodes per layer
    
    llpf = file_len(lpf) #Length of the lpf file
    count_Ss = np.zeros((1,nl)) #counter to save the line number with information for Sy
    Ss = np.zeros((nn,1)) #vector with property Ss
#    remainder = int(npl%10) #Number of elements in the last line of every property. 10 is because lpf file orders in rows of 10 elements
    
    count_Ss = []
    Ss_data = []

    for k in range(1,nl + 1):
        prop = 'Sy Layer ' + str(k)
        for j in range (1,llpf):
            aux = data2[j] #read every line
            if prop in aux:
                count_Ss.append(j)
                break
        
    # Assigns property to every node      
    for m in range(0,nl):
        aux_2 = data2[int(count_Ss[m])]
        aux_3 = data2[count_Ss[m]+1:(count_Ss[m]+int(np.ceil(npl/10))+1)]
        
        if aux_2.split()[0] == 'INTERNAL':
            for n in range(0,int(np.ceil(npl/10))):
                Ss_data.append(aux_3[n].split())    
                
        elif aux_2.split()[0] == 'CONSTANT':
            l = [float(aux_2.split()[1])] * npl
            Ss_data.append(l)    
       
        elif aux_2.split()[0] == 'OPEN/CLOSE':
            Sy_=root_name+str(m+1)+'._S1'
            Sy_file = open(Sy_,'r')
            Ss_data.append(Sy_file.readlines())
            
        else:
            print("unknown format of lpf file")
    
    Ss = list(flatten(Ss_data))
    Ss = np.asarray(Ss).astype(float)              
    return Ss

def getHeadResults(root_name, totim):
    hds = root_name + '.hds'
    nn = getNumberOfNodes(root_name)
    # Gets the head information using Flopy
    hds_file = bf.HeadUFile(hds)
    head = np.reshape(hds_file.get_data(totim=totim),nn)                      
    return head

def getConcResults(root_name,totim):
    Conc = root_name + '.con'
    nn = getNumberOfNodes(root_name)
    # Gets the head information using Flopy
    Conc_file = bf.HeadUFile(Conc)
    C = np.reshape(Conc_file.get_data(totim=totim),nn)                      
    return C

def getTopElevation(root_name):
    dis = str(root_name) + '.dis'
    dis_file = open(dis,'r') #open lpf file
    data2 = dis_file.readlines() #read lpf file
    nl = getNumberOfLayers(root_name) #gets number of layers
    nn = getNumberOfNodes(root_name) #gets number of nodes
    npl = getNumberOfNodesPerLayer(root_name) #number of nodes per layer
    
    ldis = file_len(dis) #Length of the dis file
    count_Top = np.zeros((1,nl)) #counter to save the line number with information for Sy
    Top = np.zeros((nn,1)) #vector with property Sy
#    remainder = int(npl%10) #Number of elements in the last line of every property. 10 is because lpf file orders in rows of 10 elements
    
    count_Top = []
    Top_data = []

    for k in range(1,nl + 1):
        prop = 'Top elevation Layer ' + str(k)
        for j in range (1,ldis):
            aux = data2[j] #read every line
            if prop in aux:
                count_Top.append(j)
                break
        
    # Assigns property to every node      
    for m in range(0,nl):
        aux_2 = data2[int(count_Top[m])]
        aux_3 = data2[count_Top[m]+1:(count_Top[m]+int(np.ceil(npl/10))+1)]
        
        if aux_2.split()[0] == 'INTERNAL':
            for n in range(0,int(np.ceil(npl/10))):
                Top_data.append(aux_3[n].split())    
                
        elif aux_2.split()[0] == 'CONSTANT':
            l = [float(aux_2.split()[1])] * npl
            Top_data.append(l)    
       
#        elif aux_2.split()[0] == 'OPEN/CLOSE':
#            Sy=root_name+str(m+1)+'._kx'
#            Sy_file = open(Sy_,'r')
#            Sy_data.append(Sy_file.readlines())
#            
        else:
            print("unknown format of lpf file")
    
    Top = list(flatten(Top_data))
    Top = np.asarray(Top).astype(float)              

    return Top

def getBottomElevation(root_name):
    dis = str(root_name) + '.dis'
    dis_file = open(dis,'r') #open lpf file
    data2 = dis_file.readlines() #read lpf file
    nl = getNumberOfLayers(root_name) #gets number of layers
    nn = getNumberOfNodes(root_name) #gets number of nodes
    npl = getNumberOfNodesPerLayer(root_name) #number of nodes per layer
    
    ldis = file_len(dis) #Length of the dis file
    count_Bot = np.zeros((1,nl)) #counter to save the line number with information for Sy
    Bot = np.zeros((nn,1)) #vector with property Sy
#    remainder = int(npl%10) #Number of elements in the last line of every property. 10 is because lpf file orders in rows of 10 elements
    
    count_Bot = []
    Bot_data = []

    for k in range(1,nl + 1):
        prop = 'Bottom elevation Layer ' + str(k)
        for j in range (1,ldis):
            aux = data2[j] #read every line
            if prop in aux:
                count_Bot.append(j)
                break
        
    # Assigns property to every node      
    for m in range(0,nl):
        aux_2 = data2[int(count_Bot[m])]
        aux_3 = data2[count_Bot[m]+1:(count_Bot[m]+int(np.ceil(npl/10))+1)]
        
        if aux_2.split()[0] == 'INTERNAL':
            for n in range(0,int(np.ceil(npl/10))):
                Bot_data.append(aux_3[n].split())    
                
        elif aux_2.split()[0] == 'CONSTANT':
            l = [float(aux_2.split()[1])] * npl
            Bot_data.append(l)    
       
#        elif aux_2.split()[0] == 'OPEN/CLOSE':
#            Sy=root_name+str(m+1)+'._kx'
#            Sy_file = open(Sy_,'r')
#            Sy_data.append(Sy_file.readlines())
#            
        else:
            print("unknown format of lpf file")
    
    Bot = list(flatten(Bot_data))
    Bot = np.asarray(Bot).astype(float)              

    return Bot

def getNodalAreas(root_name):
    dis = str(root_name) + '.dis'
    dis_file = open(dis,'r') #open lpf file
    data2 = dis_file.readlines() #read lpf file
    nl = getNumberOfLayers(root_name) #gets number of layers
    nn = getNumberOfNodes(root_name) #gets number of nodes
    npl = getNumberOfNodesPerLayer(root_name) #number of nodes per layer

    ldis = file_len(dis) #Length of the dis file
    count_n_area = np.zeros((1,nl)) #counter to save the line number with information for Sy
    n_area = np.zeros((nn,1)) #vector with property Sy

    count_n_area = []
    n_area_data = []

    for k in range(1,nl + 1):
        prop = 'Nodal Areas'
        for j in range (1,ldis):
            aux = data2[j] #read every line
            if prop in aux:
                count_n_area.append(j)
                break
    
    # Assigns property to every node      
    for m in range(0,nl):
        aux_2 = data2[int(count_n_area[m])]
        aux_3 = data2[count_n_area[m]+1:(count_n_area[m]+int(np.ceil(npl/10))+1)]
        
        if aux_2.split()[0] == 'INTERNAL':
            for n in range(0,int(np.ceil(npl/10))):
                n_area_data.append(aux_3[n].split())    
                
        elif aux_2.split()[0] == 'CONSTANT':
            l = [float(aux_2.split()[1])] * npl
            n_area_data.append(l)    
       
    #        elif aux_2.split()[0] == 'OPEN/CLOSE':
    #            Sy=root_name+str(m+1)+'._kx'
    #            Sy_file = open(Sy_,'r')
    #            Sy_data.append(Sy_file.readlines())
    #            
        else:
            print("unknown format of lpf file")
    
    n_area = list(flatten(n_area_data))
    n_area = np.asarray(n_area).astype(float)             

    return n_area

