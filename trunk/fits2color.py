# This code convert the r g b fits image to a color jpeg or png
# this is modified from the corresponding IDL code. For papers, see Lupton et al 2004.
# Jiangang Hao @ Fermilab, 9/15/2012

try:
    import scipy.ndimage as nd
    import Image
    import numpy as np
    import pyfits as pf
except ImportError:
    print "Error: missing one of the libraries (numpy, PIL, scipy, pyfits)"
    sys.exit()


def arcsinhFit(colorImg=None,nonlinearity=3.):
    """
    mapping the ADU to the range 0 - 1
    """
    R = colorImg[:,:,0]
    G = colorImg[:,:,1]
    B = colorImg[:,:,2]
    Nx = R.shape[0]
    Ny = R.shape[1]
    radius = (R + G + B)/3.
    radius = radius + (radius == 0).astype('b')
    if nonlinearity == 0.:
        val = radius
    else:
        val = np.arcsinh(radius*nonlinearity)/nonlinearity
    FitColorImg = np.zeros((Nx,Ny,3))
    FitColorImg[:,:,0] = R*val/radius
    FitColorImg[:,:,1] = G*val/radius
    FitColorImg[:,:,2] = B*val/radius
    return FitColorImg 

def fit2box(colorImg,origin=[0.,0.,0.]):
    Nx = colorImg[:,:,0].shape[0]
    Ny = colorImg[:,:,0].shape[1]
    originArray = np.zeros((Nx,Ny,3))
    for i in range(3):
        originArray[:,:,i] = origin[i]
    posDist = 1 - originArray
    boxedColors = colorImg
    factor = np.maximum((colorImg[:,:,0]/posDist[:,:,0]),(colorImg[:,:,1]/posDist[:,:,1]))
    factor = np.maximum(factor,(colorImg[:,:,2]/posDist[:,:,2]))
    factor = np.clip(factor,1., factor.max())
    for j in range(3):
        boxedColors[:,:,j] = colorImg[:,:,j]/factor
    return boxedColors


def float2byte(Img):
    byteImg = np.clip(Img*256.0,0,255)
    return byteImg.astype('byte')


def scaleRGB(colorImg,scale=[4.9,5.7,7.8]):
    Nx = colorImg.shape[0]
    Ny = colorImg.shape[1]
    scaleColorImg = np.zeros(colorImg.shape)
    for i in range(3):
        scaleColorImg[:,:,i] = colorImg[:,:,i]*scale[i]
    return scaleColorImg


def makeColorImg(gImg,rImg,iImg):
    scale= [0.025,0.025,0.045]
    nonlinearity= 3.0
    resizefactor= 0.5
    smoothScale = 1.5
    gImg = nd.filters.gaussian_filter(gImg, smoothScale)
    rImg = nd.filters.gaussian_filter(rImg, smoothScale)
    iImg = nd.filters.gaussian_filter(iImg, smoothScale)
    Nx = gImg.shape[0]
    Ny = gImg.shape[1]
    rgbImg = np.zeros((Nx,Ny,3))
    rgbImg[:,:,0] = iImg
    rgbImg[:,:,1] = rImg
    rgbImg[:,:,2] = gImg

    rgbImg = scaleRGB(rgbImg,scale=scale)
    rgbImg = arcsinhFit(rgbImg,nonlinearity=nonlinearity)
    rgbImg = fit2box(rgbImg,origin=[0,0,-10])
    rgbImg = float2byte(rgbImg)

    RGBimage = Image.fromarray(rgbImg,'RGB')
    return RGBimage


if __name__ == "__main__":
    from fits2color import *
    gImg = pf.getdata('fpC-100006-g1-0062.fit.gz')
    rImg = pf.getdata('fpC-100006-r1-0062.fit.gz')
    iImg = pf.getdata('fpC-100006-i1-0062.fit.gz')
    img = makeColorImg(gImg,rImg,iImg)
