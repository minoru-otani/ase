import numpy as npy
from math import sqrt, exp

def tri2full(M, UL='L'):
    """UP='L' => fill upper triangle from lower triangle
       such that M=M^d"""
    nbf = len(M)
    if UL == 'L':
        for i in range(nbf - 1):
            M[i, i:] = M[i:, i].conj()
    elif UL == 'U':
        for i in range(nbf - 1):
            M[i:, i] = M[i, i:].conj()

def dagger(matrix):
    return npy.conj(matrix.T)

def rotate_matrix(h, u):
    return npy.dot(u.T.conj(), npy.dot(h, u))

def get_subspace(matrix, index):
    """Get the subspace spanned by the basis function listed in index"""
    return matrix.take(index, 0).take(index, 1)   

permute_matrix = get_subspace

def normalize_rot(matrix, S=None):
    """Normalize column vectors.

    ::

      <matrix[:,i]| S |matrix[:,i]> = 1

    """
    for col in matrix.T:
        if S is None:
            col /= npy.linalg.norm(col)
        else:
            col /= npy.sqrt(npy.dot(col.conj(), npy.dot(S, col)))

def subdiagonalize(h_ii, s_ii, index_j):
    nb = h_ii.shape[0]
    nb_sub = len(index_j)
    h_sub_jj = get_subspace(h_ii, index_j)
    s_sub_jj = get_subspace(s_ii, index_j)
    e_j, v_jj = npy.linalg.eig(npy.linalg.solve(s_sub_jj, h_sub_jj))
    normalize_rot(v_jj, s_sub_jj) # normalize: <v_j|s|v_j> = 1
    permute_list = npy.argsort(e_j.real)
    e_j = npy.take(e_j, permute_list)
    v_jj = npy.take(v_jj, permute_list, axis=1)
    
    #setup transformation matrix
    c_ii = npy.identity(nb, complex)
    for i in xrange(nb_sub):
        for j in xrange(nb_sub):
            c_ii[index_j[i], index_j[j]] = v_jj[i, j]

    h1_ii = rotate_matrix(h_ii, c_ii)
    s1_ii = rotate_matrix(s_ii, c_ii)

    return h1_ii, s1_ii, c_ii, e_j

def cutcoupling(h, s, index_n):
    for i in index_n:
        s[:, i] = 0.0
        s[i, :] = 0.0
        s[i, i] = 1.0
        Ei = h[i, i]
        h[:, i] = 0.0
        h[i, :] = 0.0
        h[i, i] = Ei

def fermidistribution(energy, kt):
    #fermi level is fixed to zero
    return 1.0 / (1.0 + npy.exp(energy / kt) )

def fliplr(a):
    length=len(a)
    b = [0] * length
    for i in range(length):
        b[i] = a[length - i - 1]
    return b

def plot_path(energy):
    import pylab
    pylab.plot(npy.real(energy), npy.imag(energy), 'b--o')
    pylab.show()
    

def function_integral(function, calcutype):
    #return the integral of the 'function' on 'intrange'    
    #the function can be a value or a matrix, arg1,arg2 are the possible
    #parameters of the function
    
    intctrl = function.intctrl
    if calcutype == 'eqInt':
        intrange = intctrl.eqintpath
        tol = intctrl.eqinttol
        if hasattr(function.intctrl, 'eqpath_radius'):
            radius = function.intctrl.eqpath_radius
        else:
            radius = -1
        if hasattr(function.intctrl, 'eqpath_origin'):
            origin = function.intctrl.eqpath_origin
        else:
            origin = 1000
    elif calcutype == 'neInt':
        intrange = intctrl.neintpath
        tol = intctrl.neinttol
        radius = -1
        origin = 1000
    elif calcutype == 'locInt':
        intrange = intctrl.locintpath
        tol = intctrl.locinttol
        if hasattr(function.intctrl, 'locpath_radius'):
            radius = function.intctrl.locpath_radius
        else:
            radius = -1
        if hasattr(function.intctrl, 'locpath_origin'):
            origin = function.intctrl.locpath_origin
        else:
            origin = 1000
    trace = 0    
    a = 0.
    b = 1.

    #Initialize with 13 function evaluations.
    c = (a + b) / 2
    h = (b - a) / 2
    realmin = 2e-308

    s = [.942882415695480, sqrt(2.0/3),
         .641853342345781, 1/sqrt(5.0), .236383199662150]
    s1 = [0] * len(s)
    s2 = [0] * len(s)
    for i in range(len(s)):
        s1[i] = c - s[i] * h
        s2[i] = c + fliplr(s)[i] * h
    x0 = [a] + s1 + [c] + s2 + [b]

    s0 = [.0158271919734802, .094273840218850, .155071987336585,
          .188821573960182,  .199773405226859, .224926465333340]
    w0 = s0 + [.242611071901408] + fliplr(s0)
    w1 = [1, 0, 0, 0, 5, 0, 0, 0, 5, 0, 0, 0, 1]
    w2 = [77, 0, 432, 0, 625, 0, 672, 0, 625, 0, 432, 0, 77]
    for i in range(len(w1)):
        w1[i] = w1[i] / 6.0
        w2[i] = w2[i] / 1470.0
                                                        
    dZ = [intrange[:len(intrange) - 1], intrange[1:]]
    hmin = [0] * len(dZ[1])

    path_type = []
    for i in range(len(intrange) - 1):
        rs = npy.abs(dZ[0][i] - origin)
        re = npy.abs(dZ[1][i] - origin)
        if abs(rs - radius) < 1.0e-8 and abs(re - radius) < 1.0e-8:
            path_type.append('half_circle')
        else:
            path_type.append('line')
   
    for i in range(len(dZ[1])):
        if path_type[i] == 'half_circle':
            dZ[0][i] = 0
            dZ[1][i] = npy.pi
    for i in range(len(dZ[1])):
        dZ[1][i] = dZ[1][i] - dZ[0][i]
        hmin[i] = realmin / 1024 * abs(dZ[1][i])


    temp = npy.array([[1] * 13, x0]).transpose()
    
    Zx = npy.dot(temp, npy.array(dZ))
      
    Zxx = []
    for i in range(len(intrange) - 1):
        for j in range(13):
            Zxx.append(Zx[j][i])

    ns = 0
    ne = 12
    if path_type[0] == 'line':
        yns = function.calgfunc(Zxx[ns], calcutype)
    elif path_type[0] == 'half_circle':
        energy = origin + radius * npy.exp((npy.pi - Zxx[ns + i]) * 1.j)
        yns = -1.j * radius * npy.exp(-1.j* Zxx[ns +i])* function.calgfunc(energy, calcutype)        
    fcnt = 0
    

    for n in range(len(intrange)-1):
        # below evaluate the integral and adjust the tolerance
        Q1pQ0 = yns * (w1[0] - w0[0])
        Q2pQ0 = yns * (w2[0] - w0[0])
        fcnt = fcnt + 12
        for i in range(1,12):
            if path_type[n] == 'line':
                yne = function.calgfunc(Zxx[ns + i], calcutype)
            elif path_type[n] == 'half_circle':
                energy = origin + radius * npy.exp((npy.pi -Zxx[ns + i]) * 1.j)
                yne = -1.j * radius * npy.exp(-1.j * Zxx[ns + i])* function.calgfunc(energy, calcutype)
            Q1pQ0 += yne * (w1[i] - w0[i])
            Q2pQ0 += yne * (w2[i] - w0[i])

        # Increase the tolerance if refinement appears to be effective
        r = npy.abs(Q2pQ0) / npy.abs(Q1pQ0 + realmin)
        dim = npy.product(r.shape)
        r = npy.sum(r) / dim
        if r > 0 and r < 1:
            thistol = tol / r
        else:
            thistol = tol
        if path_type[n] == 'line':
            yne = function.calgfunc(Zxx[ne], calcutype)
        elif path_type[n] == 'half_circle':
            energy = origin + radius * npy.exp((npy.pi -Zxx[ne]) * 1.j)
            yne = -1.j * radius * npy.exp(-1.j * Zxx[ne])* function.calgfunc(energy, calcutype)
        #Call the recursive core integrator
       
        Qk, xpk, wpk, fcnt, warn = quadlstep(function, Zxx[ns],
                                            Zxx[ne], yns, yne,
                                            thistol, trace, fcnt,
                                            hmin[n], calcutype, path_type[n],
                                            origin, radius)
        if n == 0:
            Q = npy.copy(Qk)
            Xp = xpk[:]
            Wp = wpk[:]
        else:
            Q += Qk
            Xp = Xp[:-1] + xpk
            Wp = Wp[:-1] + [Wp[-1] + wpk[0]] + wpk[1:]
        if warn == 1:
            print 'warning: Minimum step size reached,singularity possible'
        elif warn == 2:
            print 'warning: Maximum function count excced; singularity likely'
        elif warn == 3:
            print 'warning: Infinite or Not-a-Number function value encountered'
        else:
            pass
        
        ns += 13
        ne += 13
        yns = npy.copy(yne)
      
    return Q,Xp,Wp,fcnt

def quadlstep(f, Za, Zb, fa, fb, tol, trace, fcnt, hmin, calcutype,
                                                   path_type, origin, radius):
    #Gaussian-Lobatto and Kronrod method
    #QUADLSTEP Recursive core routine for integral
    #input parameters:
    #      f      ----------   function, here we just use the module calgfunc
    #                          to return the value, if wanna use it for
    #                          another one, change it
    #     Za, Zb  ----------   the start and end point of the integral
    #     fa, fb  ----------   the function value on Za and Zb
    #     fcnt    ----------   the number of the funtion recalled till now
    #output parameters:
    #      Q      ----------   integral
    #     Xp      ----------   selected points
    #     Wp      ----------   weight
    #    fcnt     ----------   the number of the function recalled till now

    maxfcnt = 10000

    # Evaluate integrand five times in interior of subintrval [a,b]
    Zh = (Zb - Za) / 2.0
    if abs(Zh) < hmin:
        # Minimun step size reached; singularity possible
        Q = Zh * (fa + fb)
        if path_type == 'line':
            Xp = [Za, Zb]
        elif path_type == 'half_circle':
            Xp = [origin + radius * npy.exp((npy.pi - Za) * 1.j),
                                      origin + radius * npy.exp((npy.pi - Zb) * 1.j)]
        Wp = [Zh, Zh]
        warn = 1
        return Q, Xp, Wp, fcnt, warn
    fcnt += 5
    if fcnt > maxfcnt:
        #Maximum function count exceed; singularity likely
        Q = Zh * (fa + fb)
        if path_type == 'line':
            Xp = [Za, Zb]
        elif path_type == 'half_circle':
            Xp = [origin + radius * npy.exp((npy.pi - Za) * 1.j),
                                      origin + radius * npy.exp((npy.pi - Zb) * 1.j)]
        Wp = [Zh, Zh]
        warn = 2
        return Q, Xp, Wp, fcnt, warn
    x = [0.18350341907227,   0.55278640450004,   1.0,
         1.44721359549996,   1.81649658092773];
    Zx = [0] * len(x)
    y = [0] * len(x)
    for i in range(len(x)):
        x[i] *= 0.5
        Zx[i] = Za + (Zb - Za) * x[i]
        if path_type == 'line':
            y[i] = f.calgfunc(Zx[i], calcutype)
        elif path_type == 'half_circle':
            energy = origin + radius * npy.exp((npy.pi - Zx[i]) * 1.j)
            y[i] = f.calgfunc(energy, calcutype)
    #Four point Lobatto quadrature
    s1 = [1.0, 0.0, 5.0, 0.0, 5.0, 0.0, 1.0]
    s2 = [77.0, 432.0, 625.0, 672.0, 625.0, 432.0, 77.0]
    Wk = [0] * 7
    Wp = [0] * 7
    for i in range(7):
        Wk[i] = (Zh / 6.0) * s1[i]
        Wp[i] = (Zh / 1470.0) * s2[i]
    if path_type == 'line':
        Xp = [Za] + Zx + [Zb]
    elif path_type == 'half_circle':
        Xp = [Za] + Zx + [Zb] 
        for i in range(7):
            factor = -1.j * radius * npy.exp(1.j * (npy.pi - Xp[i]))
            Wk[i] *= factor
            Wp[i] *= factor
            Xp[i] = origin + radius * npy.exp((npy.pi - Xp[i]) * 1.j)
    Qk = fa * Wk[0] + fb * Wk[6]
    Q = fa * Wp[0] + fb * Wp[6]
    for i in range(1, 6):
        Qk += y[i-1] * Wk[i]
        Q  += y[i-1] * Wp[i]
    if npy.isinf(npy.max(npy.abs(Q))):
        Q = Zh * (fa + fb)
        if path_type == 'line':
            Xp = [Za, Zb]
        elif path_type == 'half_circle':
            Xp = [origin + radius * npy.exp((npy.pi - Za) * 1.j),
                                      origin + radius * npy.exp((npy.pi - Zb) * 1.j)]
        Wp = [Zh, Zh]
        warn = 3
        return Qk, Xp, Wp, fcnt, warn
    else:
        pass
    if trace:
        print fcnt, real(Za), imag(Za), abs(Zh)
    #Check accurancy of integral over this subinterval
    XXk = [Xp[0], Xp[2], Xp[4], Xp[6]]
    WWk = [Wk[0], Wk[2], Wk[4], Wk[6]]
    YYk = [fa, y[1], y[3], fb]
    if npy.max(npy.abs(Qk - Q)) <= tol:
        warn = 0
        return Q, XXk, WWk, fcnt, warn
    #Subdivide into six subintevals
    else:
        Q, Xk, Wk, fcnt, warn = quadlstep(f, Za, Zx[1], fa, YYk[1],
                                           tol, trace, fcnt, hmin,
                                               calcutype, path_type,
                                                origin, radius)

        Qk, xkk, wkk, fcnt, warnk = quadlstep(f, Zx[1],
                          Zx[3], YYk[1], YYk[2], tol, trace, fcnt, hmin,
                                             calcutype, path_type,
                                             origin, radius)
        Q += Qk
        Xk = Xk[:-1] + xkk
        Wk = Wk[:-1] + [Wk[-1] + wkk[0]] + wkk[1:]
        warn = max(warn, warnk)
        
        Qk, xkk, wkk, fcnt, warnk = quadlstep(f, Zx[3], Zb, YYk[2], fb,
                                           tol, trace, fcnt, hmin,
                                                   calcutype, path_type,
                                                   origin, radius)
        Q += Qk
        Xk = Xk[:-1] + xkk
        Wk = Wk[:-1] + [Wk[-1] + wkk[0]] + wkk[1:]
        warn = max(warn, warnk)
    return Q, Xk, Wk, fcnt, warn

def mytextread0(filename):
    num = 0
    df = file(filename)
    df.seek(0)
    for line in df:
        if num == 0:
            dim = line.strip().split(' ')
            row = int(dim[0])
            col = int(dim[1])
            mat = npy.empty([row, col])
        else:
            data = line.strip().split(' ')
            if len(data) == 0 or len(data)== 1:
                break
            else:
                for i in range(len(data)):
                    mat[num - 1, i] = float(data[i])
        num += 1
    return mat

def mytextread1(filename):
    num = 0
    df = file(filename)
    df.seek(0)
    data = []
    for line in df:
        tmp = line.strip()
        if len(tmp) != 0: 
            data.append(float(tmp))
        else:
            break
    dim = int(sqrt(len(data)))
    mat = npy.empty([dim, dim])
    for i in range(dim):
        for j in range(dim):
            mat[i, j] = data[num]
            num += 1
    return mat

def mytextwrite1(filename, mat):
    num = 0
    df = open(filename,'w')
    df.seek(0)
    dim = mat.shape[0]
    if dim != mat.shape[1]:
        print 'matwirte, matrix is not square'
    for i in range(dim):
        for j in range(dim):
            df.write('%20.20e\n'% mat[i, j])
    df.close()
