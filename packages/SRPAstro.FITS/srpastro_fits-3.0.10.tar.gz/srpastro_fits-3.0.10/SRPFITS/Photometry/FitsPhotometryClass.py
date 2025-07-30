""" Utility functions and classes for SRP

Context : SRP
Module  : PhotometryClass.py
Version : 1.0.0
Author  : Stefano Covino
Date    : 02/10/2024
E-mail  : stefano.covino@inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks :

History : (02/10/2024) First version.
"""

#import os
import numpy as np
from astropy.table import Table
import sep
from SRPFITS.Photometry.ApyPhot import ApyPhot
#from SRPFITS.Photometry.DaoPhot import DaoPhot
from SRPFITS.Fits.GetData import GetData
#from .GetHeader import GetHeader
#from SRPFITS.Fits.GetWCS import GetWCS
#from .GetHeaderValue import GetHeaderValue
#from . import FitsConstants as FitsConstants
#from SRPFITS.GetFWHM import GetFWHM
from SRPFITS.Photometry.Counts2Mag import Counts2Mag
#from SRPFITS.Frames.SourceObjectsClass import SourceObjects
#from SRPFITS.Frames.SexObjectClass import SexObjects
#from SRPFITS.Frames.DAOObjectClass import DAOObjects
#from SRPFITS.Frames.Pixel2WCS import Pixel2WCS
#from astropy import log
#log.setLevel('WARNING')

class FitsPhotometry:
    def __init__ (self, fitsfile, objlist, exptime=1., airmass=1., extcoeff=0., zeropoint=(25.0,0.0), level=3):
        self.Fitsfile = fitsfile
        self.ObjList = objlist
        self.Exptime = exptime
        self.Airmass = airmass
        self.ExtCoeff = extcoeff
        self.Zeropoint = zeropoint
        self.Level = level

    def GetImageData (self, extension=0):
        try:
            self.Data = GetData (self.Fitsfile, extension)[0]
            return True
        except:
            return False
        
    def GetObjPos (self):
        try:
            iftab = Table.read(self.ObjList,format='ascii')
            self.X = iftab.columns[1]
            self.Y = iftab.columns[2]
            return True
        except:
            return False
    
    
    def SexPhotometry (self):
        # From here: https://python.hotexamples.com/it/examples/sep/-/set_extract_pixstack/python-set_extract_pixstack-function-examples.html
        data = self.Data
        #
        try:
            bkg = sep.Background(data)
        except ValueError:
            data = data.byteswap(True).newbyteorder()
            bkg = sep.Background(data)
        bkg.subfrom(data)
        #
        sources = sep.extract(data, self.Level * bkg.globalrms)
        #
        sources = Table(sources)
        # Calculate the ellipticity
        sources['ellipticity'] = 1.0 - (sources['b'] / sources['a'])
        # Fix any value of theta that are invalid due to floating point rounding
        # -pi / 2 < theta < pi / 2
        sources['theta'][sources['theta'] > (np.pi / 2.0)] -= np.pi
        sources['theta'][sources['theta'] < (-np.pi / 2.0)] += np.pi
        # Calculate the kron radius
        kronrad, krflag = sep.kron_radius(data, sources['x'], sources['y'],
            sources['a'], sources['b'], sources['theta'], 6.0)
        sources['flag'] |= krflag
        sources['kronrad'] = kronrad
        # Calculate the equivilent of flux_auto
        flux, fluxerr, flag = sep.sum_ellipse(data, sources['x'], sources['y'],
            sources['a'], sources['b'], np.pi / 2.0, 2.5 * kronrad, subpix=1, err=self.Level * bkg.globalrms)
        sources['flux'] = flux
        sources['fluxerr'] = fluxerr
        sources['flag'] |= flag
        # Calculate the FWHMs of the stars:
        fwhm = 2.0 * (np.log(2) * (sources['a'] ** 2.0 + sources['b'] ** 2.0)) ** 0.5
        sources['fwhm'] = fwhm
        # Cut individual bright pixels. Often cosmic rays
        sources = sources[fwhm > 1.0]
        # Measure the flux profile
        flux_radii, flag = sep.flux_radius(data, sources['x'], sources['y'],
            6.0 * sources['a'], [0.25, 0.5, 0.75], normflux=sources['flux'], subpix=5)
        sources['flag'] |= flag
        sources['fluxrad25'] = flux_radii[:, 0]
        sources['fluxrad50'] = flux_radii[:, 1]
        sources['fluxrad75'] = flux_radii[:, 2]
        # Calculate the windowed positions
        sig = 2.0 / 2.35 * sources['fluxrad50']
        xwin, ywin, flag = sep.winpos(data, sources['x'], sources['y'], sig)
        sources['flag'] |= flag
        sources['xwin'] = xwin
        sources['ywin'] = ywin
        # Calculate the average background at each source
        bkgflux, fluxerr, flag = sep.sum_ellipse(bkg.back(), sources['x'], sources['y'],
            sources['a'], sources['b'], np.pi / 2.0, 2.5 * sources['kronrad'], subpix=1)
        background_area = (2.5 * sources['kronrad']) ** 2.0 * sources['a'] * sources['b'] * np.pi # - masksum
        sources['background'] = bkgflux
        sources['background'][background_area > 0] /= background_area[background_area > 0]
        # Update the catalog to match fits convention instead of python array convention
        sources['x'] += 1.0
        sources['y'] += 1.0
        sources['xpeak'] += 1
        sources['ypeak'] += 1
        sources['xwin'] += 1.0
        sources['ywin'] += 1.0
        sources['theta'] = np.degrees(sources['theta'])
        #
        # Exptime
        flux, fluxerr = flux/self.Exptime, fluxerr/self.Exptime
        # Convert to magnitudes
        # Zero point
        mag,magerr = Counts2Mag(flux,fluxerr,self.Zeropoint[0],self.Zeropoint[1])
        # Airmass
        mag = mag - self.ExtCoeff*self.Airmass
        #
        sources['mag'] = mag
        sources['emag'] = magerr
        self.SexResults = sources
        return Table([sources['x'],sources['y'],flux,fluxerr,mag,magerr],names=('X','Y','Flux','eFlux','Mag','eMag'))
        
        
    def ApyPhotometry (self, rds=(5,10,15),backgr=True,gain=1.,ron=0.):
            flux,fluxerr = ApyPhot (self.X,self.Y,self.Data,rds,backgr,gain,ron)
            # Exptime
            flux, fluxerr = flux/self.Exptime, fluxerr/self.Exptime
            # Zero point
            mag, emag = Counts2Mag (flux,fluxerr,self.Zeropoint[0],self.Zeropoint[1])
            # Airmass
            mag = mag - self.ExtCoeff*self.Airmass
            return Table([self.X,self.Y,flux,fluxerr,mag,emag],names=('X','Y','Flux','eFlux','Mag','eMag'))

                       
    #def DaoPhotometry (self, rds=(5,10,15),backgr=True,gain=1.,ron=0.,skyalg='mmm'):
    #        flux,fluxerr = DaoPhot (self.X,self.Y,self.Data,rds,backgr,gain,ron,skyalg)
    #        return Table([self.X,self.Y,flux,fluxerr],names=('X','Y','Flux','eFlux'))

