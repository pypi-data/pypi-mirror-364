import os
import re
import subprocess
import sys
import tempfile
import zipfile
from collections import defaultdict
from pathlib import Path
from types import ModuleType
from urllib.request import urlretrieve
from tqdm import tqdm
import json

TEMP_PACKAGES = [
    (
        "https://repo1.maven.org/maven2/jakarta/jms/jakarta.jms-api/2.0.3/jakarta.jms-api-2.0.3.jar",
        [
            "javax.",
            "jakarta.",
        ],
    )
]


PACKAGE_PREFIXES = [
    # standard lib
    "java.util.ArrayList",
    # "java.",
    # "jdk.",
    # "javax.",
]

OUTPUT_DIR = Path(__file__).parent / "java"
OUTPUT_PATH_CLASSES = OUTPUT_DIR / "classes.py"
OUTPUT_PATH_FIELDS  = OUTPUT_DIR / "fields.py"
OUTPUT_PATH_METHODS = OUTPUT_DIR / "methods.py"

# ---- CLASS  PARENTS ----------------------------------
def get_class_parents_jar(class_name: str, classpath: str) -> list[str]:
    try:
        result = subprocess.run(
            ["javap", "-classpath", classpath, class_name],
            capture_output=True,
            text=True,
            timeout=3,
        )
        lines = result.stdout.splitlines()
        for line in lines:
            line = line.strip()
            if line.startswith("public") and ("class" in line or "interface" in line):
                parts = line.split()
                parents = []
                if "extends" in parts:
                    idx = parts.index("extends")
                    base = parts[idx + 1].strip("{,")
                    if base != "Object":
                        parents.append(base)
                if "implements" in parts:
                    idx = parts.index("implements")
                    interfaces = [p.strip(",{") for p in parts[idx + 1 :]]
                    parents.extend(interfaces)
                return parents
    except Exception:
        pass
    return []


def get_class_parents(class_name: str) -> list[str]:
    try:
        result = subprocess.run(
            ["javap", class_name],
            capture_output=True,
            text=True,
            timeout=3,
        )
        lines = result.stdout.splitlines()
        for line in lines:
            line = line.strip()
            if line.startswith("public") and ("class" in line or "interface" in line):
                parts = line.split()
                parents = []
                if "extends" in parts:
                    idx = parts.index("extends")
                    base = parts[idx + 1].strip("{,")
                    if base != "Object":
                        parents.append(base)
                if "implements" in parts:
                    idx = parts.index("implements")
                    interfaces = [p.strip(",{") for p in parts[idx + 1 :]]
                    parents.extend(interfaces)
                return parents
    except Exception:
        pass
    return []


# ---- CLASS  PARENTS ----------------------------------


# ----  METHOD INFO ----------------------------------


def extract_return_type(signature: str) -> str:
    match = re.match(r"public\s+(?:static\s+)?([^\s]+)\s+\w+\(", signature)
    if match:
        return match.group(1)
    return "void"


def extract_method_info(class_name: str, classpath: str) -> list[dict]:
    try:
        result = subprocess.run(
            ["javap", "-p", "-classpath", classpath, class_name],
            capture_output=True,
            text=True,
            timeout=5,
        )
        lines = result.stdout.splitlines()
        methods = []

        for line in lines:
            line = line.strip()
            if not line or not line.startswith(("public", "private", "protected")):
                continue
            # match signature
            match = re.match(r".*\s+([a-zA-Z0-9_<>[\].]+)\(([^)]*)\)", line)
            if not match:
                continue

            return_type = extract_return_type(line)

            try:
                name = match.group(1)
                param_str = match.group(2).strip()
                param_types = [p.strip() for p in param_str.split(",") if p.strip()]
                methods.append(
                    {
                        "name": name,
                        "parameters": param_types,
                        "signature": line,
                        "return_type": return_type,
                    }
                )
            except Exception:
                continue
        return methods
    except Exception:
        return []


# ----  METHOD INFO ----------------------------------


# ----- TEMPORARY PACKAGES -----------------------------
def download_temp_packages(temp_dir: Path) -> list[tuple[str, list[str]]]:
    jar_paths = []
    for url, packages in TEMP_PACKAGES:
        filename = url.split("/")[-1]
        local_path = temp_dir / filename
        urlretrieve(url, local_path)
        jar_paths.append((str(local_path), packages))
    return jar_paths


def list_classes_from_jar(jar_path: str, packages_prefixes: list[str]) -> list[str]:
    class_names = []
    with zipfile.ZipFile(jar_path) as jar:
        for entry in jar.namelist():
            if entry.endswith(".class") and not entry.startswith("META-INF/") and "$" not in entry:
                if entry.startswith("classes/"):
                    entry = entry[len("classes/") :]
                class_name = entry.removesuffix(".class").replace("/", ".")
                if any(class_name.startswith(prefix) for prefix in packages_prefixes):
                    class_names.append(class_name)
    return class_names


# ----- TEMPORARY PACKAGES -----------------------------

# ---- JAVA STDLIB -------------------------------------


def find_java_home() -> str:
    try:
        return subprocess.check_output(["/usr/libexec/java_home"]).decode().strip()
    except Exception:
        fallback = "/opt/homebrew/opt/openjdk/libexec/openjdk.jdk/Contents/Home"
        if os.path.isdir(fallback):
            return fallback
        raise RuntimeError("Cannot determine JAVA_HOME")


def list_classes_from_modules(package_prefixes: list[str] = PACKAGE_PREFIXES) -> list[tuple[str, str]]:
    all_classpaths = []
    all_classes = []

    java_home = find_java_home()
    if java_home:
        jmods_path = Path(java_home) / "jmods"
        if jmods_path.exists():
            for jmod in jmods_path.glob("*.jmod"):
                classes = list_classes_from_jar(jmod, package_prefixes)
                all_classpaths.append(str(jmod))
                all_classes.extend((cls, str(jmod)) for cls in classes)
    return all_classes


# ---- JAVA STDLIB -------------------------------------


def extract_fields(class_name: str, classpath: str) -> list[dict]:
    try:
        result = subprocess.run(
            ["javap", "-p", "-classpath", classpath, class_name],
            capture_output=True,
            text=True,
            timeout=5,
        )
        fields = []
        for line in result.stdout.splitlines():
            line = line.strip()
            if (
                line.startswith("public")
                or line.startswith("protected")
                or line.startswith("private")
            ):
                if ";" in line and "(" not in line:  # simple field
                    parts = line.split()
                    if len(parts) >= 3:
                        field_type = parts[-2]
                        field_name = parts[-1].rstrip(";")
                        fields.append((field_name, field_type))
        return fields
    except Exception:
        return []


type_header_classes = """from typing import Dict, List, TypedDict

class ClassInfo(TypedDict):
    parents: List[str]

ClassesDict = Dict[str, Dict[str, ClassInfo]]"""

type_header_fields = """from typing import Dict, List, TypedDict

class FieldInfo(TypedDict):
    name: str
    type: str
    signature: str

FieldsDict = Dict[str, Dict[str, List[FieldInfo]]]"""

type_header_methods = """from typing import Dict, List, TypedDict

class MethodInfo(TypedDict):
    name: str
    parameters: List[str]
    return_type: str
    signature: str

MethodsDict = Dict[str, Dict[str, List[MethodInfo]]]"""


def freeze(o):
    if isinstance(o, defaultdict):
        return {k: freeze(v) for k, v in o.items()}
    if isinstance(o, dict):
        return {k: freeze(v) for k, v in o.items()}
    if isinstance(o, list):
        return [freeze(v) for v in o]
    return o

def write_py_dict(path: Path, var_name: str, type_header: str, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    # Convert JSON literals to Python literals safely (word boundaries)
    json_str = json.dumps(data, ensure_ascii=False, indent=4)
    json_str = re.sub(r'\\btrue\\b', 'True', json_str)
    json_str = re.sub(r'\\bfalse\\b', 'False', json_str)
    json_str = re.sub(r'\\bnull\\b', 'None', json_str)

    with path.open("w", encoding="utf-8") as f:
        f.write("# Auto-generated by java_generate.py\n# flake8: noqa\n\n")
        f.write(type_header.rstrip() + "\n\n")
        f.write(f"{var_name} = {json_str}\n")
        f.write("\n")


def generate_file():
    classes_data = defaultdict(dict)  # pkg -> class -> {"parents": [...]}
    fields_data  = defaultdict(dict)  # pkg -> class -> [FieldInfo]
    methods_data = defaultdict(dict)  # pkg -> class -> [MethodInfo]

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        jar_paths = download_temp_packages(tmp_path)

        for jar_path, packages in jar_paths:
            classes = list_classes_from_jar(jar_path, packages)

            for class_name in tqdm(classes, desc=f"Analyzing {os.path.basename(jar_path)}"):
                pkg, cls = class_name.rsplit(".", 1)

                classes_data[pkg][cls] = {"parents": get_class_parents_jar(class_name, str(jar_path))}
                fields_data[pkg][cls]  = extract_fields(class_name, str(jar_path))
                methods_data[pkg][cls] = extract_method_info(class_name, str(jar_path))

    all_classes = list_classes_from_modules()
    for cls_full, cp in tqdm(all_classes, desc="Analyzing Java stdlib classes"):
        pkg, cls = cls_full.rsplit(".", 1)

        classes_data[pkg][cls] = {"parents": get_class_parents(cls_full)}
        fields_data[pkg][cls]  = extract_fields(cls_full, cp)
        methods_data[pkg][cls] = extract_method_info(cls_full, cp)

    classes_data = freeze(classes_data)
    fields_data  = freeze(fields_data)
    methods_data = freeze(methods_data)

    write_py_dict(OUTPUT_PATH_CLASSES, "JAVA_CLASSES: ClassesDict", type_header_classes, classes_data)
    write_py_dict(OUTPUT_PATH_FIELDS,  "JAVA_FIELDS: FieldsDict",  type_header_fields,  fields_data)
    write_py_dict(OUTPUT_PATH_METHODS, "JAVA_METHODS: MethodsDict", type_header_methods, methods_data)


def deep_getsizeof(o, seen=None):
    if seen is None:
        seen = set()

    obj_id = id(o)
    if obj_id in seen:
        return 0
    seen.add(obj_id)

    size = sys.getsizeof(o)

    if isinstance(o, dict):
        size += sum(deep_getsizeof(k, seen) + deep_getsizeof(v, seen) for k, v in o.items())
    elif isinstance(o, list | tuple | set | frozenset):
        size += sum(deep_getsizeof(i, seen) for i in o)
    elif isinstance(o, ModuleType):
        return 0

    return size


def check_size():
    from java.classes  import JAVA_CLASSES
    from java.fields  import JAVA_FIELDS
    from java.methods  import JAVA_METHODS
    print(f"Size of JAVA_CLASSES: {deep_getsizeof(JAVA_CLASSES) / (1024*1024):.4f} MB")
    print(f"Size of JAVA_FIELDS: {deep_getsizeof(JAVA_FIELDS) / (1024*1024):.4f} MB")
    print(f"Size of JAVA_METHODS: {deep_getsizeof(JAVA_METHODS) / (1024*1024):.4f} MB")


if __name__ == "__main__":
    generate_file()
    check_size()
