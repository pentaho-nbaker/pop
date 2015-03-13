from RepoAnalyzer import RepoAnalyzer
import re
import mysql.connector
# import psycopg2

class BranchDiffAnalyzer(RepoAnalyzer):

    meaningfulFileExtensions = [".java", ".js", ".xml", ".css", ".txt"]

    def __init__(self):
        self.fileRegistry = {}
        self.filesForCommit = {}


    def __shouldIndexFile( self, path ):
        if( path.find(".") == -1 ):
            return
        path.rindex(".")

        ext = path[path.rindex("."):]
        return ext in self.meaningfulFileExtensions



    def createFileHit( self, path, action, additions, deletions):

        if( not self.__shouldIndexFile( path )):
            return

        return FileHit(path, action, additions, deletions)


    def analyze(self, name, repo, stable, active):

        self.repo = repo


        if active not in repo.references or stable not in repo.references:
            print "Missing branches for " + name
            return

        active_branch = repo.references[active]
        stable_branch = repo.references[stable]

        self.process_commit( active_branch.commit, stable_branch.commit)


        cnx = mysql.connector.connect(user='nbaker', password='BT7Mv2CZimRw',
                          host='10.100.2.164',
                          database='githubreporting')
        cursor = cnx.cursor()

        repository_select = "SELECT id FROM repositories WHERE name = '%s'" % (name)
        repository_insert = "INSERT into repositories(name) VALUES ('%s')" % (name)

        cursor.execute(repository_select)
        result = cursor.fetchall()
        if(len(result) > 0):
            repository_id = result[0][0]
        else:
            cursor.execute(repository_insert)
            repository_id = cursor.lastrowid

        branch_select = "SELECT id FROM branches WHERE name = '%s' and repository_id = %s"
        branch_insert = "INSERT into branches(name, repository_id) VALUES ('%s', %s)"

        cursor.execute(branch_select % (stable, repository_id))
        result = cursor.fetchall()
        if(len(result) > 0):
            stable_branch_id = result[0][0]
        else:
            cursor.execute(branch_insert % (stable, repository_id))
            stable_branch_id = cursor.lastrowid


        cursor.execute(branch_select % (active, repository_id))
        result = cursor.fetchall()
        if(len(result) > 0):
            active_branch_id = result[0][0]
        else:
            cursor.execute(branch_insert % (active, repository_id))
            active_branch_id = cursor.lastrowid


        branch_diff_select = "SELECT id FROM branch_diff where branch_a_id = %s AND branch_b_id = %s AND repository_id = %s"
        branch_diff_insert = "INSERT INTO branch_diff(branch_a_id, branch_b_id, repository_id) values(%s,%s,%s)"

        cursor.execute(branch_diff_select % (stable_branch_id, active_branch_id, repository_id))
        result = cursor.fetchall()
        if(len(result) > 0):
            branch_diff_id = result[0][0]
        else:
            cursor.execute(branch_diff_insert % (stable_branch_id, active_branch_id, repository_id))
            branch_diff_id = cursor.lastrowid


        commit_insert = ("INSERT into commits(repository_id, branch_diff_id, sha, author, commit_date, message, jira) "
        "values(%s, %s, %s, %s, FROM_UNIXTIME('%s'), %s, %s)")
        for commit, files in self.filesForCommit.iteritems():
            print str(commit)
            message = commit.message
            match = re.search('^\[(.*)\]', message)
            jira = match.group(1) if match is not None else None

            cursor.execute(commit_insert, (repository_id, branch_diff_id, commit.hexsha, commit.author.email, commit.committed_date, message, jira))
            commit_id = cursor.lastrowid

            for f in files:
                files_select = "SELECT id FROM files WHERE path = '%s' and repository_id = %s"
                files_insert = "INSERT into files(path, repository_id) VALUES ('%s', %s)"

                cursor.execute(files_select % (f.path, repository_id))
                result = cursor.fetchall()
                if(len(result) > 0):
                    file_id = result[0][0]
                else:
                    cursor.execute(files_insert % (f.path, repository_id))
                    file_id = cursor.lastrowid

                commit_files = ("INSERT INTO commit_files(commit_id, file_id, action, lines_added, lines_removed) "
                                "VALUES(%s,%s,'%s',%s,%s)")
                cursor.execute(commit_files % (commit_id, file_id, f.action, f.additions, f.deletions))

                print "\t%s: %s %d %d" % (f.action, f.path, f.additions, f.deletions)


        cnx.close()


    def process_commit(self, commit, parentCommit):
        print "processing: "+  str(commit)

        self.filesForCommit[commit] = []

        if( commit == parentCommit ):
            return
        if( parentCommit is not None ):
            try:
                self.repo.git.merge_base( commit, self.repo.commit(parentCommit), "--is-ancestor")
                # commit closes an ongoing merge. Return and it will be handled by the outside run of this function
                return
            except:
                # Not an ancestor, process and continue on with chain.
                pass

        newParentCommit = commit.parents[0] if len(commit.parents) > 0 else None
        if( len(commit.parents) > 1 ): # Merge commit

            # walk one side until a commit is an ancestor of the other.
            self.process_commit(commit.parents[1], newParentCommit )
        elif newParentCommit is not None:
            diff = newParentCommit.diff(commit, create_patch=True)
            self.processDiff( diff, commit )

        if newParentCommit is not None:
            self.process_commit(newParentCommit, parentCommit)

    def processDiff(self, diff, commit):
        for diffItem in diff:

            if diffItem.a_blob is None and diffItem.b_blob is None:
                print "Error processing diff for commit: " + str(commit)
                return

            path = diffItem.a_blob.path if diffItem.a_blob != None else diffItem.b_blob.path


            if( diffItem.new_file ):
                action = "A"
            elif( diffItem.deleted_file ):
                action = "D"
            elif( diffItem.renamed ):
                action = "R"
            else:
                action = "M"

            if diffItem.diff is not None:
                additions = len(re.findall("\\n\\+", diffItem.diff))
                deletions = len(re.findall("\\n\\-", diffItem.diff))


            file = self.createFileHit(path, action, additions, deletions)
            if( file == None ):
                return

            self.filesForCommit[commit].append(file)


class FileHit:
    actions = {"M": "modified", "A": "added", "R": "removed", "D": "deleted"}
    def __init__(self, path, action, additions, deletions):
        if( action not in self.actions ):
            raise "Action not expected"

        self.path = path
        self.action = action  # M, A, R, D
        self.additions = additions
        self.deletions = deletions

