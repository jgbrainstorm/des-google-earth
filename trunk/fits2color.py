# This code convert the r g b fits image to a color jpeg or png
# this is modified from the corresponding IDL code. For papers, see Lupton et al 2004.
# Jiangang Hao @ Fermilab, 9/15/2012

try:
    import scipy.ndimage as nd
    import Image
    import numpy as np
    import pyfits as pf
    import glob as gl
    import ImageEnhance
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
    boxedColors = np.zeros((Nx,Ny,3))
    for i in range(3):
        originArray[:,:,i] = origin[i]
    posDist = 1 - originArray
    factor = np.maximum((colorImg[:,:,0]/posDist[:,:,0]),(colorImg[:,:,1]/posDist[:,:,1]))
    factor = np.maximum(factor,(colorImg[:,:,2]/posDist[:,:,2]))
    factor = np.clip(factor,1., factor.max())
    for j in range(3):
        boxedColors[:,:,j] = colorImg[:,:,j]/factor
    return boxedColors


def float2byte(Img):
    byteImg = np.zeros((Img.shape[0],Img.shape[1],3))
    for i in range(3):
        byteImg[:,:,i] = np.clip(Img[:,:,i]*256.0,0,255)
    return np.uint8(byteImg)


def scaleRGB(colorImg,scale= [0.025,0.025,0.045]):
    Nx = colorImg.shape[0]
    Ny = colorImg.shape[1]
    scaleColorImg = np.zeros(colorImg.shape)
    for i in range(3):
        scaleColorImg[:,:,i] = colorImg[:,:,i]*scale[i]
        skylevel = np.median(scaleColorImg[:,:,i])
        scaleColorImg[:,:,i]=np.clip(scaleColorImg[:,:,i],skylevel,3000)-skylevel   
    return scaleColorImg

def shiftRGB(redF,greenF,blueF,blueshiftr=0,blueshiftc=0,greenshiftr=0,greenshiftc=0,redshiftr=0,redshiftc=0,ext=None):
    """
    this code shift the pixels of three r, g, b images. Using g image as reference and shift the other two images. It will return the shifted r,g,b images.
    each row goes along ra direction
    each col goes along dec direction
    CRVAL1 ; ra direction
    CRVAL2: dec direction
    """
    blueHdr = pf.getheader(blueF,ext)
    greenHdr = pf.getheader(greenF,ext)
    redHdr = pf.getheader(redF,ext)
    bluerow = blueHdr['crval1']*3600./0.27
    bluecol = blueHdr['crval2']*3600./0.27
    greenrow = greenHdr['crval1']*3600./0.27
    greencol = greenHdr['crval2']*3600./0.27
    redrow = redHdr['crval1']*3600./0.27
    redcol = redHdr['crval2']*3600./0.27
    """
    col0=int(blueHdr['datasec'].split('[')[1].split(']')[0].split(',')[0].split(':')[0])-1
    col1=int(blueHdr['datasec'].split('[')[1].split(']')[0].split(',')[0].split(':')[1]) 
    row0=int(blueHdr['datasec'].split('[')[1].split(']')[0].split(',')[1].split(':')[0])-1
    row1=int(blueHdr['datasec'].split('[')[1].split(']')[0].split(',')[1].split(':')[1]) 
    """
    blue = pf.getdata(blueF,ext)
    green = pf.getdata(greenF,ext)
    red = pf.getdata(redF,ext)

    ctgreenrow = (bluerow+greenrow+redrow)/3.
    ctgreencol = (bluecol+greencol+redcol)/3.
    blue = nd.shift(blue,[bluerow - ctgreenrow+blueshiftr,bluecol-ctgreencol+blueshiftc],mode='nearest',order=1)
    green = nd.shift(green,[greenrow - ctgreenrow+greenshiftr,greencol-ctgreencol+greenshiftc],mode='nearest',order=1)
    red = nd.shift(red,[redrow - ctgreenrow+redshiftr, redcol-ctgreencol+redshiftc],mode='nearest',order=1)
    return red,green,blue
    #return blue[row0:row1,col0:col1],green[row0:row1,col0:col1],red[row0:row1,col0:col1]




def makeColorImg(red,green,blue,scale=[0.025,0.025,0.045],smoothScale=2.,nonlinearity=3.0,colorOrigin=[0,0,0]):
    blue = nd.filters.gaussian_filter(blue, smoothScale)
    green = nd.filters.gaussian_filter(green, smoothScale)
    red = nd.filters.gaussian_filter(red, smoothScale)
    Nx = blue.shape[0]
    Ny = blue.shape[1]
    rgbImg = np.zeros((Nx,Ny,3))
    rgbImg[:,:,0] = red
    rgbImg[:,:,1] = green
    rgbImg[:,:,2] = blue        
    rgbImg = scaleRGB(rgbImg,scale=scale)
    rgbImg = arcsinhFit(rgbImg,nonlinearity=nonlinearity)
    rgbImg = fit2box(rgbImg,origin=colorOrigin)
    rgbByte = float2byte(rgbImg)
    RGB = Image.fromarray(rgbByte,'RGB')
    #RGB.show()
    return RGB

def colorImg(redF,greenF,blueF,blueshiftr=0,blueshiftc=0,greenshiftr=0,greenshiftc=0,redshiftr=0,redshiftc=0,ext=None,scale= [0.025,0.025,0.045],nonlinearity=3.,smooth=2.):
    red,green,blue = shiftRGB(redF,greenF,blueF,blueshiftr,blueshiftc,greenshiftr,greenshiftc,redshiftr,redshiftc,ext)
    #bsky = np.median(blue)
    #gsky = np.median(green)
    #rsky = np.median(red)
    #blue = np.clip(blue,bsky,3000)-bsky
    #green = np.clip(green,gsky,3000)-gsky
    #red = np.clip(red,rsky,3000)-rsky
    img = makeColorImg(red,green,blue,scale,nonlinearity=nonlinearity,smoothScale=smooth)
    return img



if __name__ == "__main__":
    from fits2color import *

    #---des stripe 82 test field ---
    blueF = gl.glob('/home/jghao/research/data/des_realimage/des-google/testrun_stripe82_fieldF_g/*.fits')
    greenF = gl.glob('/home/jghao/research/data/des_realimage/des-google/testrun_stripe82_fieldF_r/*.fits')
    redF = gl.glob('/home/jghao/research/data/des_realimage/des-google/testrun_stripe82_fieldF_i/*.fits')
    blueF.sort()
    greenF.sort()
    redF.sort()
    
    scale= [0.025/8.,0.025/8.,0.05/8.]
    img=colorImg(redF[i],greenF[i],blueF[i],scale= [0.025/8.,0.025/8.,0.05/8.])
    ehImg=ImageEnhance.Contrast(img)
    newImg=ehImg.enhance(1.2)
    newImg.crop((5,10,2044,4090))
    newImg.save('descolor.png',format='PNG')

    #img.save('/home/jghao/research/data/des_realimage/des-google/testrun_stripe82_color/'+blueF[i][-30:-21]+'.PNG',format="PNG")
    
    #-----sdss image ----
    redF = 'fpC-100006-i1-0062.fit.gz'
    greenF = 'fpC-100006-r1-0062.fit.gz'
    blueF = 'fpC-100006-g1-0062.fit.gz'
    
    scale=[0.025,0.025,0.045]
    img=colorImg(redF,greenF,blueF,scale=[0.025,0.025,0.045])

    #---des image ---
    redF='DECam_00137345_corrected.fits'
    blueF='DECam_00137330_corrected.fits'
    greenF='DECam_00137338_corrected.fits'
    ext='S4'
    blue,green,red = shiftRGB(blueF,greenF,redF,ext=ext)
    gsky = np.median(blue)
    rsky = np.median(green)
    isky = np.median(red)
    blue = np.clip(blue,gsky,50000)-gsky
    green = np.clip(green,rsky,50000)-rsky
    red = np.clip(red,isky,50000)-isky
        
    scale= [0.025/8.,0.025/8.,0.05/8.]
    img = makeColorImg(blue,green,red,scale,nonlinearity=5.)
    ehImg=ImageEnhance.Contrast(img)
    newImg=ehImg.enhance(1.2)
    
    # des coadd --
    redF='image_z.fits'
    greenF='image_i.fits'
    blueF='image_r.fits'
    size = 0.5
    img=colorImg(redF,greenF,blueF,scale=[0.03*size,0.03*size,0.04*size],nonlinearity=2.)
    imgnew=img.crop(box = (100,100,4000,2000))
    imgnew.save('coadd1.png')
    imgnew=img.crop(box = (200,2400,4000,4300))
    imgnew.save('coadd2.png')
    
    # des coadd stripe 82--
    redF='/home/jghao/research/data/des_realimage/des-google/stripe82_coadd/image_z_small.fits'
    greenF='/home/jghao/research/data/des_realimage/des-google/stripe82_coadd/image_i_small.fits'
    blueF='/home/jghao/research/data/des_realimage/des-google/stripe82_coadd/image_r_small.fits'
    size = 0.23
    img=colorImg(redF,greenF,blueF,scale=[0.049*size,0.039*size,0.04*size],nonlinearity=8,smooth=1.2)
    img.save('des_coadd_stripe82.png')
   

    #------slice image into smaller ones ----
    dir = '/home/jghao/research/data/des_realimage/des-google/stripe82_coadd/'
    voiletF=dir+'image_g.fits'
    redF=dir+'image_z.fits'
    greenF=dir+'image_i.fits'
    blueF=dir+'image_r.fits'


def sliceImg(filename,band):
    npix = 3500
    nimg = 4
    for i in range(nimg):
        for j in range(nimg):
            print i,j
            imghdu= pf.open(filename)
            imghdu[0].data = imghdu[0].data[i*npix:(i+1)*npix,j*npix:(j+1)*npix]
            xdiff = 1750.5+j*npix - 7000.5
            ydiff = 1750.5+i*npix - 7000.5
            imghdu[0].header.update('CRPIX1',1750.5)
            imghdu[0].header.update('CRPIX2',1750.5)
            imghdu[0].header.update('NAXIS1',3500)
            imghdu[0].header.update('NAXIS2',3500)
            imghdu[0].header.update('CRVAL1',16.535-xdiff*0.27/3600.)
            imghdu[0].header.update('CRVAL2',0.8286+ydiff*0.27/3600.)
            imghdu.writeto(dir+'image_'+band+'_'+str(i)+'_'+str(j)+'.fits')

    sliceImg(redF,'z')
    sliceImg(greenF,'i')
    sliceImg(blueF,'r')
    sliceImg(voiletF,'g')
    #-----make color image ---
    nimg = 4
    for i in range(nimg):
        for j in range(nimg):
            print i,j
            redF = dir+'image_z_'+str(i)+'_'+str(j)+'.fits'
            greenF = dir+'image_i_'+str(i)+'_'+str(j)+'.fits'
            blueF = dir+'image_r_'+str(i)+'_'+str(j)+'.fits'
            size = 0.15
            img=colorImg(redF,greenF,blueF,scale=[0.049*size,0.039*size,0.04*size],nonlinearity=8,smooth=1.2)
            ehImg=ImageEnhance.Contrast(img)
            newImg=ehImg.enhance(1.2)
            newImg.save(dir+'image_rgb_'+str(i)+'_'+str(j)+'.png')


            
    #----combine back
    blank_image = Image.new('RGB',(14000,14000))
    nimg = 4
    for i in range(nimg):
        for j in range(nimg):
            print i,j
            colimg = dir+'png1/image_rgb_'+str(i)+'_'+str(j)+'.png'
            im = Image.open(colimg)
            blank_image.paste(im,(j*npix,i*npix))
 
