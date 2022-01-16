import json

filename = '/Users/Craig/Documents/pythonApps/athleteAPI/files/fileList.json'

#filetype = 'StravaToken'

def jsonLoader(filetype):
    with open(filename) as f:
        fileList = json.load(f)
        inputFile = fileList[filetype]

    with open(inputFile) as f:
        #access_credentials  = json.load(f)
        fileData = json.load(f)

    return(fileData)

def jsonWriter(filetype, output):
    with open(filename) as f:
        filelist = json.load(f)
        outputFile = filelist[filetype]
        print('Writing to... ', outputFile)

    with open(outputFile, 'w') as outfile:
        json.dump(output, outfile)

#print(fileData)