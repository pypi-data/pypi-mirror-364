# 🚀 Launching the software

## 🎥 Example

To test the program, use the following commands in `📁 smiffer/`:

```sh
$ mkdir data/output/

# Launching the software.
$ smiffer -i data1EHE.pdb \
$         -p data1EHE_parameter.yml \
$         -a data/1EHE_APBS.dx \
$         -o data/output/

# Visualize using VMD (or other like PyMol, Chimera, Mol*, etc.).
$ vmd data/1EHE.pdb data/output/*.mrc
```

### 🔧 `parameter.yml`

To see what are the options you can use, check: https://smiffer.mol3d.tech/parameter/.
In this file, you can specify a lot of options to setup the software.
Here is a first example to run the software on whole **protein**:

```yml
box:
    extra_size: 5
    area_mode: whole
other:
    macromolecule: protein
```

Here is a first example to run the software specific part of an **RNA**:

```yml
box:
    area_mode: pocket_sphere
    center:
        x: 0.7
        y: -1.8
        z: 3.6
    # Integer.
    radius: 9
other:
    macromolecule: nucleic
```

> **📝 Note :**
>
> This file is not mandatory. If not used, the software is going to fall back on default parameters.
> Check https://smiffer.mol3d.tech/parameter/ for more information.

## 🔍 Describing possible parameters

| **Argument**              | **Mandatory?** | **Type and usage**     | **Description**                                                              |
| :------------------------ | :------------: | :--------------------- | :--------------------------------------------------------------------------- |
| **`-i` or `--input`**     |      Yes       | `--input file.pdb`     | The `.pdb` file that while be used<br/>to computed the properties.           |
| **`-o` or `--output`**    |      Yes       | `--output directory`   | The directory to output the results.                                         |
| **`-p` or `--parameter`** |       No       | `--parameter file.yml` | The YAML parameters file.                                                    |
| **`-a` or `--apbs`**      |       No       | `--apbs file.dx`       | The already computed APBS<br/>electrostatic grid.                            |
| **`-h` or `--help`**      |       No       | Flag                   | Display the help and exit the<br/>program.                                   |
| **`-v` or `--version`**   |       No       | Flag                   | Display the version and exit the<br/>program.                                |
| **`--verbose`**           |       No       | Flag                   | Activated a verbose mode, so more<br/>information are going to be displayed. |
