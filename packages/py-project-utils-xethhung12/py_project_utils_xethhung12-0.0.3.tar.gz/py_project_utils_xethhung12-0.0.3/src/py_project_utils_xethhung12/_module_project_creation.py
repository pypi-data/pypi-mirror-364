import sys
import shutil
import os
import importlib.resources as resources
import py_project_utils_xethhung12 as py_project
def create_project(project_name, argv: [str]):
    resourcePath=resources.files("py_project_utils_xethhung12.data")
    base = str(resourcePath._paths[0])
    data = list(resourcePath.iterdir())
    for i in data:
        print("base: ", base)
        pr = str(i)
        print("pr: ",pr)

        if os.path.isdir(pr):
            print(pr, "is directory, skipping")
            continue

        project_name_for_replacing = project_name.replace("-","_")
        fp = pr[len(base)+1:]\
            .replace("$","/")\
            .replace("___project_name___",project_name_for_replacing)
        print("fp: ",fp)
        hasSubPath = True if len(fp.split("/")) > 1 else False
        if hasSubPath:
            os.makedirs("/".join(fp.split("/")[:-1]), exist_ok=True)
        shutil.copy(pr, fp)
        with open(fp, "rt") as fin:
            with open(f"{fp}__", "wt") as fout:
                for line in fin:
                    fout.write(line.replace("___project_name___", project_name_for_replacing))
        if os.path.exist(fp):
            os.remove(fp)
        shutil.move(f"{fp}__", fp)
    print("Project initializing complete")