#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun 16 11:25:18 2024

@author: robertsoncl
"""
import re
import random
import fileinput
import shutil
import os
import time

# class for handling pre-processing of topas scripts for submission
# to batch processing systems. Includes generation of .submit and .sh files


class topasProcessor:
    # load in file
    def __init__(self, pathToFile):
        f = open(pathToFile)
        for line in f:
            if 'NumberOfHistoriesInRun' in line:
                oldnHists = re.findall(r'\d+', line)[0]
        self.file = pathToFile
        self.oldnHists = oldnHists
    # split initial topas file into smaller factors with NParticles
    # smaller by chosen factor
    # do not remove the prints, these are the writing process

    def splitFile(self, factor, outputDir='/home/robertsoncl/SplitFiles/', scriptName='topasScript'):
        file = self.file
        self.factor = factor
        # ensure appropriate file structure exists
        # make copies of original file
        for i in range(factor):
            splitFileName = outputDir+scriptName+str(i)
            try:
                shutil.copyfile(file, splitFileName)
            except FileNotFoundError:
                print('No output folder detected, generating one')
                os.system('mkdir '+str(outputDir[:-1]))
                shutil.copyfile(file, splitFileName)

            # replace particle number with number reduced by factor
            # randomise seed
            # change output to increment, otherwise sub-files would replace
            # each other

            with fileinput.input(splitFileName, inplace=True) as f:
                for line in f:
                    if 'NumberOfHistoriesInRun' in line:
                        nHists = re.findall(r'\d+', line)[0]
                        newHists = str(int(int(nHists)/factor))
                        new_line = line.replace(nHists, newHists)
                        print(new_line, end='')

                    elif 'i:Ts/Seed' in line:
                        new_line = line.replace(line, 'i:Ts/Seed = ' +
                                                str(random.randint(0, 100000))+'\n')
                        print(new_line, end='')
                    elif 'IfOutputFileAlreadyExists' in line:
                        new_line = line.replace('Overwrite', 'Increment')
                        print(new_line, end='')
                    else:
                        print(line, end='')
            # generate directory and move scripts to dedicated directory
            try:
                shutil.copyfile(splitFileName, outputDir +
                                'splitScripts/'+scriptName+str(i))
            except FileNotFoundError:
                print('No output folder detected, generating one')
                os.system('mkdir '+outputDir+'splitScripts')
                shutil.copyfile(splitFileName, outputDir +
                                'splitScripts/'+scriptName+str(i))
            # cleanup excess files
            os.system('rm '+outputDir+scriptName+'*')
            # set paths as attributes for use in further methods
            self.outputDir = outputDir
            self.scriptName = scriptName
    # produce required files for running on the HTCondor cluster
    # will be produced inside specified outputDir
    # directory in pplxintFolderPath should be the same name as outputDir
    # but with different path to get there since it's on pplxint

    def generateCondorFiles(self, pplxintFolderPath='/home/robertsonc/SplitFiles/', pplxtopas='/home/robertsonc/topas/bin/topas', pplxDataDir='~/G4Data'):
        # create bashfiles folder and scripts
        # G4 data directory defined inside those for ease
        f = open(self.outputDir+'filenames', 'w')
        for i in range(self.factor):

            bashFileName = self.outputDir + \
                'bashfiles/'+self.scriptName+str(i)+'.sh'

            bashFileName = self.outputDir + \
                'bashfiles/'+self.scriptName+str(i)+'.sh'
            try:
                bash = open(bashFileName, 'w')
            except FileNotFoundError:
                print('No bashfiles directory, generating a new one')
                os.system('mkdir ' + self.outputDir +
                          'bashfiles')
                bash = open(bashFileName, 'w')

            bash.write('#!/usr/bin/bash\n')
            bash.write('export TOPAS_G4_DATA_DIR='+pplxDataDir+'\n')
            bash.write(
                pplxtopas + ' '+pplxintFolderPath+'splitScripts/'+self.scriptName+str(i))
            bash.close()

            f.write(self.scriptName+str(i)+'.sh\n')
            # make bash scripts readable
            os.system('chmod u+x '+bashFileName)
        f.close()

        # create required output directories

        os.system('mkdir '+self.outputDir+'error')
        os.system('mkdir '+self.outputDir+'output')
        os.system('mkdir '+self.outputDir+'log')
        # create and write myjob.submit file
        sub = open(self.outputDir+'myjob.submit', 'w')

        sub.write('executable              = ' +
                  pplxintFolderPath+'bashfiles/$(filename)\n')
        sub.write('getenv                  = true\n')
        sub.write('output                  = output/results.output.$(ClusterId)\n')
        sub.write('error                   = error/results.error.$(ClusterId)\n')
        sub.write('log                     = log/results.log.$(ClusterId)\n')
        sub.write('notification            = never\n')
        sub.write('queue filename from '+pplxintFolderPath+'filenames')
        sub.close()
        self.pplxintFolderPath = pplxintFolderPath

    # def submitFiles(self, password):
    #     os.system('rsync -Pr ' +
    #               self.outputDir[:-1]+' pplxint12.physics.ox.ac.uk:')
    #     time.sleep(5)
    #     os.system(password)
    #     time.sleep(5)
    #     os.system(password)
    #     time.sleep(10)
    #     os.system('ssh pplxint12.ox.ac.uk')
    #     time.sleep(5)
    #     os.system(password)
    #     time.sleep(5)
    #     os.system(password)
    #     time.sleep(5)
    #     os.system('cd '+self.pplxintFolderPath)
    #     os.system('condor_submit myjob.submit')

    # def retrieveFiles(self, password, saveDirectory='/home/robertsoncl/SplitFiles'):

    #     os.system('rsync -Pr '+saveDirectory +
    #               ' pplxint12.physics.ox.ac.uk/SplitFiles')
    #     time.sleep(5)
    #     os.system(password)
    #     time.sleep(5)
    #     os.system(password)


tP = topasProcessor('/home/robertsoncl/topas/partrec_test')
tP.splitFile(10)
tP.generateCondorFiles()
