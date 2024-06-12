import os
import glob
from string import Template

# Properties
articles_source_dir = "/Users/tdc/dev/ghpages/esd/src/articles/*"
articles_target_dir = "/Users/tdc/dev/ghpages/esd/docs/articles/"
article_template_file = "/Users/tdc/dev/ghpages/esd/src/templates/index.html"

# Get a list of files from a particular directory. Remove subfolders.
def getFiles( basedir: str ) -> list:
    all_files_and_dirs = glob.glob(basedir)
    all_files = filter(os.path.isfile, all_files_and_dirs)
    file_list = list(all_files)
    return file_list

def getFileDetails( fileName: str ) -> map:
    # This method returns the filename, the title, the position, and the contents of the article
    details = {}
    fileContents = ""
    with open(fileName) as file:
        fileContents = file.read()
    
    # The name is the trailing part of the path
    _, fname = os.path.split(fileName)
    details['filename'] = fname

    # Each article should start with a comment containing metadata. Strip this out
    try:
        mdEndIndex = fileContents.index('-->')
        metadata = fileContents[5:mdEndIndex].splitlines()
        fileContents = fileContents[mdEndIndex+4:]

        # The article's date and sort order (or position) are in the metadata
        for mdLine in metadata:
            curDetails = mdLine.split(":")
            curKey = curDetails[0].strip()
            curValue = curDetails[1].strip()
            details[curKey] = curValue

    except Exception as exc:
        print(f"Exception encountered when parsing file {fname}: {exc}. Skipping")
        return None


    # The article's title is the same as the first <h2> header
    try:
        startIdx = fileContents.index('<h2>') + 4
        endIdx = fileContents.index('</h2>', startIdx)
        details['title'] = fileContents[startIdx:endIdx]
        details['contents'] = fileContents
        return details
    except Exception as exc2:
        print(f"Exception encountered when parsing the title from {fname}: {exc}. Skipping")
        return None

def buildNavTree( articles: list, short_length: int) -> map:
    longNavList = list()
    shortNavList = list()
    count = 0
    for curArticle in articles:
        n = curArticle['filename']
        t = curArticle['title']
        curItem = f'<a href="{n}">{t}</a><br/>'
        longNavList.append(curItem)
        if count <= short_length:
            shortNavList.append(curItem)
        count = count + 1
    return {
        'shortNavList': shortNavList,
        'longNavList': longNavList
    }

def publishArticle( tplFileName: str, article: map, navString: str, targetDir: str ) -> None:
    fileContents = ""
    with open(tplFileName) as file:
        fileContents = file.read()
    tpl = Template(fileContents)
    resolvedFile = tpl.substitute(navigation_details=navString,
                              content_details=article['contents'])
    # Write the file details
    fullFileAndPath = targetDir + article['filename']
    f = open(fullFileAndPath, "w")
    f.write(resolvedFile)
    f.close()
    print(f"Wrote file {fullFileAndPath}")

if __name__ == "__main__":
    all_article_names = getFiles(articles_source_dir)
    all_article_details = list()
    for cur_article in all_article_names:
        details = getFileDetails(cur_article)
        if details is not None:
            all_article_details.append(details)

    all_article_details.sort(key=lambda x: int(x['Position']))

    lists = buildNavTree(all_article_details, 5)
    shortNavString = "\n".join(lists['shortNavList'])

    for cur_article in all_article_details:
        publishArticle(article_template_file, cur_article, 
                       shortNavString, articles_target_dir)
    print("done")