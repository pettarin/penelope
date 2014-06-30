#!/usr/bin/env python
# -*- coding: utf-8 -*-

__license__     = 'MIT'
__author__      = 'Alberto Pettarin (alberto albertopettarin.it)'
__copyright__   = '2012-2014 Alberto Pettarin (alberto albertopettarin.it)'
__version__     = 'v2.0.0'
__date__        = '2014-06-30'
__description__ = 'dictEPUB creates a dictionary in EPUB format from a list of words'

### BEGIN changelog ###
#
# 2.0.0 2014-06-30 Moved to GitHub
# 1.02             Code write-up
# 1.01             Initial release
#
### END changelog ###

import codecs, collections, os, shutil, sqlite3, sys, uuid, zipfile

#Python2#
class dictEPUB:
#Python3#class dictEPUB3:

    NUMBER_LETTERS_PER_GROUP = 3
    NUMBER_WORDS_PER_GROUP = 128
    SPECIAL_GROUP_KEY = " "

    ### BEGIN createEPUBDictionary  ###
    # createEPUBDictionary(words, language, epubFilename)
    # creates the EPUB dictionary epubFilename
    # from the given list of words and with the given language metadatum
    def createEPUBDictionary(self, words, language, epubFilename):

        # EPUB title
        title = language.upper() + " Dictionary"

        # sort words
        words = sorted(words)

        # remove existing file
        if (os.path.exists(epubFilename)):
            os.remove(epubFilename)

        # create tmp directory
        tmpDir = "working"
        if (os.path.exists(tmpDir)):
            shutil.rmtree(tmpDir)
        os.makedirs(tmpDir)

        # create META-INF directory
        metaInfDir = tmpDir + "/META-INF"
        os.makedirs(metaInfDir)

        # create new mimetype file
        mimetypeFile = tmpDir + "/mimetype"
        f = open(mimetypeFile, "w")
        f.write("application/epub+zip")
        f.close()

        # container file
        contentFileRelative = "content.opf"
        contentFile = tmpDir + "/" + contentFileRelative

        # create new container.xml file
        containerFile = metaInfDir + "/container.xml"
        f = open(containerFile, "w") 
        f.write("<?xml version=\"1.0\"?>\n")
        f.write("<container version=\"1.0\" xmlns=\"urn:oasis:names:tc:opendocument:xmlns:container\">\n")
        f.write(" <rootfiles>\n")
        f.write("  <rootfile full-path=\"%s\" media-type=\"application/oebps-package+xml\"/>\n" % contentFileRelative)
        f.write(" </rootfiles>\n")
        f.write("</container>")
        f.close()

        # create new style.css file
        styleFile = tmpDir + "/style.css"
        f = open(styleFile, "w")
        f.write("@charset \"UTF-8\";\n")
        f.write("body {\n")
        f.write("  margin: 10px 25px 10px 25px;\n")
        f.write("}\n")  
        f.write("h1 {\n")
        f.write("  font-size: 200%;\n")
        f.write("}\n")
        f.write("p {\n")
        f.write("  margin-left: 0em;\n")
        f.write("  margin-right: 0em;\n")
        f.write("  margin-top: 0em;\n")
        f.write("  margin-bottom: 0em;\n")
        f.write("  line-height: 2em;\n")
        f.write("  text-align: justify;\n")
        f.write("}\n")
        f.write("a, a:focus, a:active, a:visited {\n")
        f.write("  color: black;\n")
        f.write("  text-decoration: none;\n")
        f.write("}\n")
        f.write("span {\n")
        #f.write("  margin: 0px 10px 0px 10px;\n")
        #f.write("  padding: 2px 2px 2px 2px;\n")
        #f.write("  border: solid 1px black;\n")
        f.write("}\n")
        #f.write("body.index {\n")
        #f.write("  margin: 10px 50px 10px 50px;\n")
        #f.write("}\n")
        #f.write("body.letter {\n")
        #f.write("  margin: 10px 50px 10px 50px;\n")
        #f.write("}\n")
        f.write("p.index {\n")
        f.write("  font-size: 150%;\n")
        f.write("}\n")
        f.write("p.letter {\n")
        f.write("  font-size: 150%;\n")
        f.write("}\n")
        f.close()

        # create groups
        groups = self.groupWords(words)

        # combine groups
        combinedGroups = self.combineGroups(groups)

        # collapse groups
        collapseGroups = self.collapseGroups(groups, combinedGroups)

        # create a map between starting letter and filename
        letterReferences = []
        groupReferences = []
        letterToIndexDict = dict()
        index = 0
        for g in sorted(combinedGroups.keys()):
            letterToIndexDict[g] = index
            index += 1

        # output group pages
        letterToGroups = collections.defaultdict(list)
        numberOfPages = len(collapseGroups)
        for i in range(numberOfPages):
            letterIndex = letterToIndexDict[collapseGroups[i][0]]
            self.outputCollapsedGroupPage(collapseGroups[i], i, numberOfPages, letterIndex, tmpDir)
            letterToGroups[letterIndex].append([i, collapseGroups[i][1], collapseGroups[i][2]])
            pageFile = "g" + str(i).zfill(5) + ".xhtml"
            groupReferences += [ pageFile ]
        
        # output letter pages
        indexReferences = []
        tocReferences = [ ["index.xhtml", "Index"] ]
        index = 0
        for g in sorted(combinedGroups.keys()):
            self.outputLetterPage(g, index, letterToGroups[index], tmpDir)
            pageFile = "l" + str(index).zfill(5) + ".xhtml"
            pageTitle = "Letter %s" % (g.upper())
            pageTitleHTML = "Letter&#160;%s" % (g.upper())

            if (g == self.SPECIAL_GROUP_KEY):
                pageTitle = "Special Characters"
                pageTitleHTML = "Special&#160;Characters"

            letterReferences += [ pageFile ]
            indexReferences += [ [pageFile, pageTitleHTML] ]
            tocReferences += [ [pageFile, pageTitle] ]
            index += 1

        # create index file
        self.outputIndexPage(indexReferences, title, tmpDir)

        # get UUID
        identifier = str(uuid.uuid4()).lower()

        # create toc file
        self.outputToc(tocReferences, identifier, title, tmpDir)

        # create opf file
        self.outputOpf(letterReferences, groupReferences, identifier, language, title, tmpDir)

        # zip epub
        self.zipEPUB(epubFilename, letterReferences, groupReferences, tmpDir)

        # delete tmp directory
        if (os.path.exists(tmpDir)):
            shutil.rmtree(tmpDir)

        return True
    ### END createEPUBDictionary ###


    ### BEGIN escape ###
    # escape(s)
    # escapes HTML sequences
    def escape(self, s):
        x = s
        x = x.replace("&", "&amp;")
        x = x.replace('"', "&quot;")
        x = x.replace("'", "&apos;")
        x = x.replace(">", "&gt;")
        x = x.replace("<", "&lt;")
        return x
    ### END escape ###


    ### BEGIN check_existence ###
    # check_existence(filename)
    # checks whether filename exists
    def check_existence(self, filename):
        if (filename == None):
            return False

        return os.path.isfile(filename)
    ### END check_existence ###


    ### BEGIN zipEPUB ###
    # zipEPUB(self, filename, letterReferences, groupReferences, tmpDir) 
    # zips directory into filename
    def zipEPUB(self, filename, letterReferences, groupReferences, tmpDir):
        tmpDir = tmpDir + '/'
        fileEPUB = zipfile.ZipFile(filename, 'w')
        fileEPUB.write(tmpDir + 'mimetype', 'mimetype', zipfile.ZIP_STORED)

        structure = [ "META-INF/container.xml", "content.opf", "toc.ncx", "style.css", "index.xhtml" ]
        for f in structure:
            fileEPUB.write(tmpDir + f, f, zipfile.ZIP_DEFLATED)

        for f in letterReferences:
            fileEPUB.write(tmpDir + f, f, zipfile.ZIP_DEFLATED)
        for f in groupReferences:
            fileEPUB.write(tmpDir + f, f, zipfile.ZIP_DEFLATED)
        fileEPUB.close()
    ### END zipEPUB ###


    ### BEGIN readWordsFromFile ###
    # readWordsFromFile(dictFilename)
    # reads the dictionary words from dictFilename,
    # assuming one word per line,
    # and returns a list containing them
    def readWordsFromFile(self, dictFilename):
        f = codecs.open(dictFilename, encoding='utf-8')
        toReturn = []
        for w in f.readlines():
            w = w.rstrip()
            if (len(w) > 0):
                toReturn += [ w ]
        f.close()
        return toReturn
    ### END readWordsFromFile ###


    ### BEGIN groupWords ###
    # groupWords(words)
    # groups the given list of words into groups of words
    # beginning with the same first NUMBER_LETTERS_PER_GROUP letters
    def groupWords(self, words):
        cutoff = self.NUMBER_LETTERS_PER_GROUP

        groups = collections.defaultdict(list)        
        for w in words:
            if (len(w) < cutoff):
                prefix = w.lower()
            else:
                prefix = w[0:cutoff].lower()
            groups[prefix].append(w)

        return groups 
    ### END groupWords ###


    ### BEGIN combineGroups ###
    # combineGroups(groups)
    # merge together groups s.t.
    # 1) all words starting with a character < 'a' go to the same (first) group
    # 2) all subsequent words are divided by starting character
    def combineGroups(self, groups):        
        combinedGroups = collections.defaultdict(list)
        for g in sorted(groups.keys()):
            if (g[0] < 'a'):
                combinedGroups[self.SPECIAL_GROUP_KEY].append(g)
            else:
                letter = g[0]
                combinedGroups[letter].append(g)
        
        return combinedGroups
    ### END combineGroups  ###


    ### BEGIN collapseGroups ###
    # collapseGroups(groups, combinedGroups)
    # merge together groups s.t.:
    # 1) all words starting with a character < 'a' go to the same (first) group
    # 2) all subsequent words are divided by starting character,
    # 3) if a group reaches NUMBER_WORDS_PER_GROUP words, new 
    # each group has at least NUMBER_WORDS_PER_GROUP
    # if starts w
    def collapseGroups(self, groups, combinedGroups):
        cutoff = self.NUMBER_WORDS_PER_GROUP
        collapsedGroups = []

        for g in sorted(combinedGroups.keys()):
            if (g == self.SPECIAL_GROUP_KEY):
                l = []
                for p in combinedGroups[g]:
                    l += groups[p]
                collapsedGroups += [ [self.SPECIAL_GROUP_KEY, self.SPECIAL_GROUP_KEY, self.SPECIAL_GROUP_KEY, l] ]
            else:
                startPrefix = combinedGroups[g][0]
                stopPrefix = startPrefix
                currentNumberWords = 0
                currentCollapsedGroupWords = []
                for p in combinedGroups[g]:
                    currentGroupNumberWords = len(groups[p])
                    if ((currentNumberWords + currentGroupNumberWords) > cutoff):
                        # close previous collapsed group
                        collapsedGroups += [ [g, startPrefix, stopPrefix, currentCollapsedGroupWords] ]

                        # start noutputPageew collapsed group
                        startPrefix = p
                        stopPrefix = startPrefix
                        currentNumberWords = currentGroupNumberWords
                        currentCollapsedGroupWords = groups[p]
                    else:
                        # append to current collapsed group
                        stopPrefix = p
                        currentNumberWords += currentGroupNumberWords
                        currentCollapsedGroupWords += groups[p]

                # close last collapsed group
                collapsedGroups += [ [g, startPrefix, stopPrefix, currentCollapsedGroupWords] ]

        return collapsedGroups
    ### END combineGroups  ###


    ### BEGIN outputIndexPage ###
    # outputIndexPage(indexReferences, tmpDir)
    # create the index page
    def outputIndexPage(self, indexReferences, title, tmpDir):
        sOUT = ""
        sOUT += "<?xml version=\"1.0\" encoding=\"utf-8\" standalone=\"no\"?>\n"
        sOUT += "<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.1//EN\" \"http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd\">\n"
        sOUT += "<html xmlns=\"http://www.w3.org/1999/xhtml\">\n"
        sOUT += " <head>\n"
        sOUT += "  <title>%s</title>\n" % (title)
        sOUT += "  <link rel=\"stylesheet\" type=\"text/css\" href=\"style.css\" />\n"
        sOUT += " </head>\n"
        sOUT += " <body class=\"index\">\n"
        sOUT += "  <h1>%s</h1>\n" % (title)

        sOUT += "   <p class=\"index\">\n"
        for f in indexReferences:
            # reference
            reference = f[0]
            # title
            title = f[1]
            sOUT += "   <span><a href=\"%s\">%s</a></span>\n" % (reference, title)
        sOUT += "   </p>"

        sOUT += " </body>\n"
        sOUT += "</html>\n"

        sOUT = sOUT.replace("</span>\n   <span>", "</span> &#8226; <span>")

        #Python2#
        sOUT = sOUT.encode("utf-8")
        #Python3#        sOUT = str(sOUT)

        fileOUT = open(tmpDir + "/index.xhtml", 'w')
        fileOUT.write(sOUT)
        fileOUT.close()
    ### END outputIndexPage ###

    ### BEGIN outputLetterPage ###
    # outputLetterPage(letter, pageIndex, listOfGroups, tmpDir)
    # create page for the given pageLetter letter
    # linking to all the pages containing groups
    # starting with letter
    def outputLetterPage(self, letter, pageIndex, listOfGroups, tmpDir):
        letter = letter.upper()
        
        pageName = tmpDir + "/l" + str(pageIndex).zfill(5) + ".xhtml"
        sOUT = ""
        sOUT += "<?xml version=\"1.0\" encoding=\"utf-8\" standalone=\"no\"?>\n"
        sOUT += "<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.1//EN\" \"http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd\">\n"
        sOUT += "<html xmlns=\"http://www.w3.org/1999/xhtml\">\n"
        sOUT += " <head>\n"
        sOUT += "  <title>Letter&#160;%s</title>\n" % (letter)
        sOUT += "  <link rel=\"stylesheet\" type=\"text/css\" href=\"style.css\" />\n"
        sOUT += " </head>\n"
        sOUT += " <body class=\"letter\">\n"

        if (letter == self.SPECIAL_GROUP_KEY):
            sOUT += "  <h1>Special&#160;Characters</h1>\n"
        else:
            sOUT += "  <h1>Letter&#160;%s</h1>\n" % (letter)

        sOUT += "   <h3><a href=\"index.xhtml\">[ Index ]</a></h3>\n"

        sOUT += "   <p class=\"letter\">"
        if (letter == self.SPECIAL_GROUP_KEY):
            for l in listOfGroups:
                p = "g" + str(l[0]).zfill(5) + ".xhtml"
                f = self.escape(l[1].upper())
                t = self.escape(l[2].upper())
                sOUT += "   <span><a href=\"%s\">Special Characters</a></span>\n" % (p)
        else:
            for l in listOfGroups:
                p = "g" + str(l[0]).zfill(5) + ".xhtml"
                f = self.escape(l[1].upper())
                t = self.escape(l[2].upper())
                sOUT += "   <span><a href=\"%s\">%s&#8211;%s</a></span>\n" % (p, f, t)
        sOUT += "   </p>"

        sOUT += "   <h3><a href=\"index.xhtml\">[ Index ]</a></h3>\n"

        sOUT += " </body>\n"
        sOUT += "</html>\n"
        
        sOUT = sOUT.replace("</span>\n   <span>", "</span> &#8226; <span>")
        
        #Python2#
        sOUT = sOUT.encode("utf-8")
        #Python3#        sOUT = str(sOUT)

        fileOUT = open(pageName, 'w')
        fileOUT.write(sOUT)
        fileOUT.close()
    ### END outputLetterPage ###

    
    ### BEGIN outputCollapsedGroupPage ###
    # outputPage(group, index, total, letterIndex, path)
    # create page for group index
    def outputCollapsedGroupPage(self, group, index, total, letterIndex, tmpDir):

        l = self.escape(group[0].upper())
        f = self.escape(group[1].upper())
        t = self.escape(group[2].upper())

        pageName = tmpDir + "/g" + str(index).zfill(5) + ".xhtml"
        sOUT = ""
        sOUT += "<?xml version=\"1.0\" encoding=\"utf-8\" standalone=\"no\"?>\n"
        sOUT += "<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.1//EN\" \"http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd\">\n"
        sOUT += "<html xmlns=\"http://www.w3.org/1999/xhtml\">\n"
        sOUT += " <head>\n"
        sOUT += "  <title>%s&#160;&#8211;&#160;%s</title>\n" % (f, t)
        sOUT += "  <link rel=\"stylesheet\" type=\"text/css\" href=\"style.css\" />\n"
        sOUT += " </head>\n"
        sOUT += " <body>\n"

        if ((group[1] == self.SPECIAL_GROUP_KEY) and (group[2] == self.SPECIAL_GROUP_KEY)):
            sOUT += "  <h1>Special&#160;Characters</h1>\n"
        else:
            sOUT += "  <h1>%s&#160;&#8211;&#160;%s</h1>\n" % (f, t)

        if (index > 0):
            prevPage = "<a href=\"g" + str(index - 1).zfill(5) + ".xhtml\">[ Prev ]</a>"
        else:
            prevPage = "<a>[ Prev ]</a>"

        upPage = "<a href=\"l" + str(letterIndex).zfill(5) + ".xhtml\">[ Letter ]</a>"
        indexPage = "<a href=\"index.xhtml\">[ Index ]</a>"

        if ((index + 1) < total):
            nextPage = "<a href=\"g" + str(index + 1).zfill(5) + ".xhtml\">[ Next ]</a>"
        else:
            nextPage = "<a>[ Next ]</a>"

        sOUT += "   <h3>%s %s %s %s</h3>\n" % (prevPage, upPage, indexPage, nextPage)

        sOUT += "  <p>"
        for s in group[3]:
            sOUT += "  <span>%s</span>\n" % (self.escape(s))
        sOUT += "  </p>"

        sOUT += "   <h3>%s %s %s %s</h3>\n" % (prevPage, upPage, indexPage, nextPage)

        sOUT += " </body>\n"
        sOUT += "</html>\n"

        sOUT = sOUT.replace("</span>\n  <span>", "</span> &#8226; <span>")

        #Python2#
        sOUT = sOUT.encode("utf-8")
        #Python3#        sOUT = str(sOUT)

        fileOUT = open(pageName, 'w')
        fileOUT.write(sOUT)
        fileOUT.close()
    ### END outputCollapsedGroupPage ###


    ### BEGIN createTOC ###
    # outputToc(tocReferences, identifier, tmpDir) 
    # create the toc.ncx file
    def outputToc(self, tocReferences, identifier, title, tmpDir):

        sOUT = ""
        
        sOUT += "<?xml version=\"1.0\" encoding=\"utf-8\" ?>\n"
        sOUT += "<!DOCTYPE ncx PUBLIC \"-//NISO//DTD ncx 2005-1//EN\" \"http://www.daisy.org/z3986/2005/ncx-2005-1.dtd\">\n"
        sOUT += "<ncx xmlns=\"http://www.daisy.org/z3986/2005/ncx/\" version=\"2005-1\">\n"
        sOUT += " <head>\n"
        sOUT += "  <meta name=\"dtb:uid\" content=\"%s\" />\n" % (identifier)
        sOUT += "  <meta name=\"dtb:depth\" content=\"1\" />\n"
        sOUT += "  <meta name=\"dtb:totalPageCount\" content=\"0\" />\n"
        sOUT += "  <meta name=\"dtb:maxPageNumber\" content=\"0\" />\n"
        sOUT += " </head>\n"
        sOUT += " <docTitle>\n"
        sOUT += "  <text>%s</text>\n" % (title)
        sOUT += " </docTitle>\n"
        sOUT += " <navMap>\n"

        playOrder = 0
        for f in tocReferences:
            # reference
            reference = f[0]
            # title
            title = f[1]

            playOrder += 1
            sOUT += " <navPoint id=\"%s\" playOrder=\"%s\">\n" % (reference, str(playOrder))
            sOUT += "  <navLabel>\n"
            sOUT += "   <text>%s</text>\n" % (title)
            sOUT += "  </navLabel>\n"
            sOUT += "  <content src=\"%s\" />\n" % (reference)
            sOUT += " </navPoint>\n"
        
        sOUT += " </navMap>\n"
        sOUT += "</ncx>\n"
             
        #Python2#
        sOUT = sOUT.encode("utf-8")
        #Python3#        sOUT = str(sOUT)
        
        fileOUT = open(tmpDir + "/toc.ncx", 'w')
        fileOUT.write(sOUT)
        fileOUT.close()
    ### END createTOC ###


    ### BEGIN outputOpf ###
    # outputOpf(self, letterReferences, groupReferences, identifier, language, tmpDir)
    # create the content.opf file
    def outputOpf(self, letterReferences, groupReferences, identifier, language, title, tmpDir):
        sOUT = ""
        sOUT += "<?xml version=\"1.0\" encoding=\"utf-8\" ?>\n"
        sOUT += "<package xmlns=\"http://www.idpf.org/2007/opf\" version=\"2.0\" unique-identifier=\"uuid_id\">\n"
        sOUT += " <metadata xmlns:opf=\"http://www.idpf.org/2007/opf\" xmlns:dc=\"http://purl.org/dc/elements/1.1/\">\n"
        sOUT += "  <dc:language>%s</dc:language>\n" % (language)
        sOUT += "  <dc:title>%s</dc:title>\n" % (title)
        sOUT += "  <dc:creator opf:role=\"aut\">dictEPUB.py</dc:creator>\n"
        sOUT += "  <dc:date opf:event=\"creation\">2012-12-29</dc:date>\n"
        sOUT += "  <dc:identifier id=\"uuid_id\" opf:scheme=\"uuid\">%s</dc:identifier>\n" % (identifier)
        sOUT += " </metadata>\n"

        sOUT += " <manifest>\n"
        sOUT += "  <item href=\"style.css\" id=\"css\" media-type=\"text/css\" />\n"
        sOUT += "  <item href=\"toc.ncx\" id=\"ncx\" media-type=\"application/x-dtbncx+xml\" />\n"
        sOUT += "  <item href=\"index.xhtml\" id=\"index.xhtml\" media-type=\"application/xhtml+xml\" />\n"
        for f in letterReferences:
            sOUT += "  <item href=\"%s\" id=\"%s\" media-type=\"application/xhtml+xml\" />\n" % (f, f)
        for f in groupReferences:
            sOUT += "  <item href=\"%s\" id=\"%s\" media-type=\"application/xhtml+xml\" />\n" % (f, f) 
        sOUT += " </manifest>" + '\n'
        
        sOUT += " <spine toc=\"ncx\">" + '\n'
        sOUT += "  <itemref idref=\"index.xhtml\" />\n"
        for f in letterReferences:
            sOUT += "  <itemref idref=\"%s\" />\n" % (f)
        for f in groupReferences:
            sOUT += "  <itemref idref=\"%s\" />\n" % (f)
        sOUT += " </spine>" + '\n'
        sOUT += "</package>" + '\n'

        #Python2#
        sOUT = sOUT.encode("utf-8")
        #Python3#        sOUT = str(sOUT)

        fileOUT = open(tmpDir + "/content.opf", 'w')
        fileOUT.write(sOUT)
        fileOUT.close()
    ### END outputOpf ###


    ### BEGIN usage ###
    # usage()
    # print script usage
    def usage(self):
        print("")
        #Python2#
        print("$ python dictEPUB.py words language")
        #Python3#        print("$ python3 dictEPUB3.py words language")
        print("")
        print("Required argument:")
        print(" words: the name of a UTF-8 plain text file containing the words of the dictionary, one word per line")
        print(" language: the code for the language of the dictionary, in ISO 639-1 format")
        print("")
        print("Examples:")
        #Python2#
        print(" $ python dictEPUB.py words.txt en")
        #Python3#        print(" $ python3 dictEPUB3.py words.txt en")
        print(" Create an EPUB file words.txt.epub containing the given list of English words")
        print("")
    ### END usage ###


    ### BEGIN main ###
    def main(self):
        
        if (len(sys.argv) > 2):
            dictFilename = sys.argv[1]
            language = sys.argv[2]

            if (self.check_existence(dictFilename)):
                epubFilename = dictFilename + ".epub"
                words = self.readWordsFromFile(dictFilename)
                self.createEPUBDictionary(words, language, epubFilename)
            else:
                self.usage()
        else:
            self.usage()
    ### END main ###


if __name__ == '__main__':
    #Python2#
    d = dictEPUB()
    #Python3#    d = dictEPUB3()
    d.main()

