# Mesh Generator

This is a collection of Python subroutines and examples that illustrate how to build a
MAS mesh.

Full documentation: https://q.predsci.com/docs/mesh_generator/


## Installation
**1)** Check python version is >= 3.5.0 with the following bash command:

```bash
$ python --version
Python 3.7.6
```

**2)** Use the package manager [pip](https://pip.pypa.io/en/stable/) to install mesh_generator package.

```bash
$ pip install mesh-generator
```


**4)** Check installation.

```bash
$ python
Python 3.7.6 (default, Jan  8 2020, 13:42:34)
[Clang 4.0.1 (tags/RELEASE_401/final)] :: Anaconda, Inc. on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> from mesh_generator import Mesh
```

## Workflow
1) Input mesh requirements.

2) `src/mesh.py` function `resolve_mesh_segments()` - Adjust the mesh segments.

3) `src/mesh.py` function `build_legacy_mesh()` - Build legacy mesh. 

4) `bin/call_psi_mesh.py`- Write a file with mesh points, cell resolution and ratio. 
Including optimizing the mesh total number of points.

5) `bin/tmp_mesh_[t/p/r].dat` `bin/mesh_header.dat` `bin/mesh_res_[t/p/r].txt` - output files.

![Screenshot](my-mkdocs/docs/images/mesh_generator_flowchart.png)


## Important Python subroutines
The most important Python subroutines for mesh generation are in mesh_generator:

  - src: (steps 1,2,3) creating adjusted and legacy mesh. 

  - bin: (step 4,5) writing output files, plotting, and optimizing mesh. 
        
## Dependencies

- The primary dependencies are the PSI tools (mesh) and Python 3.7.6.
- Python library dependencies:
    
        h5py>=2.8.0 # Minimum version 2.8.0
        pyhdf>=0.9.10 # Minimum version 0.9.10
        numpy>=1.15.2 # Minimum version 1.15.2
        tk >= 8.6.0 # Minimum version 8.6.0
        matplotlib>=3.0.0 # Minimum version 3.0.0
        python>=3.5.0 # Minimum version 3.5

## Adjusted Mesh Explained:

**Step 2** of creating a MAS mesh will adjust the mesh segments by calling the function `resolve_mesh_segements()` in 
`src/mesh.py`. This function will call the following functions (in ascending order):
```python
def resolve_mesh_segments(self):
    """
    Step 2 of building a mesh. Returns the adjusted mesh.
    """
    self._resolve_mesh_segments_overlap_region()  
    self._resolve_mesh_segments_narrow_region() 
    self._resolve_mesh_segments_ds()  
    if self.periodic: 
        self._periodic_case()

    return self
```

- 1) `_resolve_mesh_segments_overlap_region()`:

    Check if there is mesh segments are overlapping. If so, it will always keep the segment with the
    lower resolution.

- 2) `_resolve_mesh_segments_narrow_region()`:

    Remove all small mesh segments that are 4 or less points. And instead tag the small segment domain to the
    segment adjacent to it that has the smaller ds.


- 3) `_resolve_mesh_segments_ds()`:

    Make the current mesh continuous. Set a ds0 and ds1 for each segment.
    Meaning, ds0 is the beginning resolution and ds1 is the resolution at the end of the segment.


- 4) `_periodic_case()`

    If mesh is periodic `_periodic_case` will adjust the begin and last segments so the adjusted mesh
    will be periodic.


### Example  
Mesh input `test/ar_test.py` theta test #1: 
```python
MeshSegment.DEFAULT_BG_REGION_RATIO = 1.06
mesh = Mesh(0.00, numpy.pi, False)
mesh.insert_mesh_segment(MeshSegment(1.10, 1.40, 0.01))
mesh.insert_mesh_segment(MeshSegment(1.30, 1.90, 0.02))
mesh.insert_mesh_segment(MeshSegment(0.40, 2.80, 0.04))
```
![Screenshot](my-mkdocs/docs/images/step2plot.png)


## Legacy Mesh Explained:
`build legacy mesh()` function in `src/mesh.py`. Here we take the adjusted_mesh segments 
and calculate the segments total number of points, domain (length), and ratio. 
The calculations to solve legacy mesh segments are in src/mesh_segments.
`build_legacy_mesh() ` adds a layer of complexity since it solves the legacy mesh iteratively.
Each time a mesh segment is *undershooting* the legacy mesh is recalculated.

## Example:
For example: theta test #1 in unit_test.py:
Requirements (mesh input):
    
```python
MeshSegment.DEFAULT_BG_REGION_RATIO = 1.06
mesh = Mesh(0.00, numpy.pi, False)
mesh.insert_mesh_segment(MeshSegment(1.10, 1.40, 0.01))
mesh.insert_mesh_segment(MeshSegment(1.30, 1.90, 0.02))
mesh.insert_mesh_segment(MeshSegment(0.40, 2.80, 0.04))
return mesh
```

**Adjusted mesh results**:
```python
{
  "lower_bnd": 0.0,
  "upper_bnd": 3.141592653589793,
  "periodic": false,
  "phi_shift": 0.0,
  "BG_RATIO": 1.06,
  "segment_list": [
    {
      "s0": 0.0,
      "s1": 0.4,
      "ds0": Infinity,
      "ds1": 0.04,
      "var_ds_ratio": 1.06,
      "ratio": 0.9433962264150942
    },
    {
      "s0": 0.4,
      "s1": 1.1,
      "ds0": 0.04,
      "ds1": 0.01,
      "var_ds_ratio": 1.03,
      "ratio": 0.970873786407767
    },
    {
      "s0": 1.1,
      "s1": 1.4,
      "ds0": 0.01,
      "ds1": 0.01,
      "var_ds_ratio": 1.03,
      "ratio": 1.0
    },
    {
      "s0": 1.4,
      "s1": 1.9,
      "ds0": 0.01,
      "ds1": 0.02,
      "var_ds_ratio": 1.03,
      "ratio": 1.03
    },
    {
      "s0": 1.9,
      "s1": 2.8,
      "ds0": 0.02,
      "ds1": 0.04,
      "var_ds_ratio": 1.03,
      "ratio": 1.03
    },
    {
      "s0": 2.8,
      "s1": 3.141592653589793,
      "ds0": 0.04,
      "ds1": Infinity,
      "var_ds_ratio": 1.06,
      "ratio": 1.06
    }
  ]
}
```

**Legacy mesh results**:
```python
{
  "lower_bnd": 0.0,
  "upper_bnd": 3.141592653589793,
  "periodic": false,
  "phi_shift": 0.0,
  "BG_RATIO": 1.06,
  "segment_list": [
    {
      "s0": 0.0,
      "s1": 0.4,
      "ratio": 0.5583947769151176,
      "num_points": 10
    },
    {
      "s0": 0.4,
      "s1": 1.1,
      "ratio": 0.32522615237693164,
      "num_points": 38
    },
    {
      "s0": 1.1,
      "s1": 1.4,
      "ratio": 1.0,
      "num_points": 30
    },
    {
      "s0": 1.4,
      "s1": 1.749403232925598,
      "ratio": 2.0,
      "num_points": 24
    },
    {
      "s0": 1.749403232925598,
      "s1": 1.9,
      "ratio": 1.0,
      "num_points": 8
    },
    {
      "s0": 1.9,
      "s1": 2.5988064658511965,
      "ratio": 2.0,
      "num_points": 24
    },
    {
      "s0": 2.5988064658511965,
      "s1": 2.8,
      "ratio": 1.0,
      "num_points": 6
    },
    {
      "s0": 2.8,
      "s1": 3.141592653589793,
      "ratio": 1.5036302589913606,
      "num_points": 7
    }
  ]
}
```

![](my-mkdocs/docs/images/theta_mesh_test_1.png)

# Example 1D Mesh
   `/test/create_mesh.py`
   - This an example for creating a 1D mesh. Including 4 steps of creating a mesh.
    
- Read the comments inside the example python scripts for more details.

## Edit the python script: `/test/create_mesh.py`


- **Step 1** : Input mesh requirements. Make sure to specify:
    
    Mesh:
    
  - Set `lower_bnd` and `upper_bnd` limits of mesh.
  
  - Set `periodic`.
  
  - Set `DEFAULT_BG_REGION_RATIO` - Ratio in areas without ds constraint. (Optional)
  
  - Set `DEFAULT_FG_REGION_RATIO` - Ratio in areas with ds constraint. (Optional)
  
   Mesh segment:
    
  - Set `s0` and `s1` for segment domain limits.
  
  - Set `ds` to the resolution you want.
  
  - Set `var_ds_ratio` as segment maximum cell to cell mesh expansion ratio. (Optional)

```python 
# default ratio in regions you do not care about. (Default is 1.06)
MeshSegment.DEFAULT_BG_REGION_RATIO = 1.06 

# default ratio in regions you do care about. (Default is 1.03) 
MeshSegment.DEFAULT_FG_REGION_RATIO = 1.03  

# mesh boundaries and if periodic
mesh = Mesh(lower_bnd=0.00, upper_bnd=numpy.pi, periodic=False) 

# Mesh segment requirements:
# s0 - segment begin, s1- segment end, ds- mesh spacing
# (Optional) var_ds_ratio- the maximum ratio between each point in the mesh segment. 
mesh.insert_mesh_segment(MeshSegment(s0=1.10, s1=1.40, ds=0.01, var_ds_ratio=1.05))
mesh.insert_mesh_segment(MeshSegment(s0=1.30, s1=1.90, ds=0.02))
mesh.insert_mesh_segment(MeshSegment(s0=0.40, s1=2.80, ds=0.04, var_ds_ratio=1.02))

input_mesh = mesh.json_dict()
```  

- **Step 2**: Get adjusted mesh and save it as a dictionary.      
        
```python 
adjusted_mesh = mesh.resolve_mesh_segments().json_dict()
```

- **Step 3**: Get legacy mesh and save it as a dictionary.    
        
```python 
legacy_mesh = mesh.build_legacy_mesh().json_dict()
```   

- **Step 4**: Create mesh_res.dat file with mesh points location, resolution and cell-to-cell ratio. 
```python 
# show_plot = True (return a mesh spacing plot of mesh_res.txt) plotting is done by matplotlib.
# save_plot = True (saves the plot as a png in "plots" folder.
# dir_name = the directory which will dump the output and mesh_res files. 
create_psi_mesh(adjusted_mesh, legacy_mesh, mesh_type="t", dir_name=os.getcwd(),
     output_file_name="tmp_mesh_t.dat", mesh_res_file_name="mesh_res_t.dat",
     save_plot=True, show_plot=False, save_plot_path=os.getcwd(), plot_file_name="t_mesh_spacing.png", 
     input_mesh=input_mesh)
```
- **Step 5**: Call the fortran code. Inspect the results:

    - mesh_res_t.dat - file with mesh points. 
    
    - tmp_mesh_t.dat - file with legacy mesh results. 
    
    - Setting get_plot =True will return a plot of mesh_res_t.dat. The plot below is an example.     

![Screenshot](my-mkdocs/docs/images/create_mesh_ex.png)



# Example 3D Mesh

Similar to the example of building a 1D Mesh. We can build a 3D Mesh. 

In this example, the 3D Mesh is in polar coordinates (theta, phi, r). 

## Option #1
First, build the 3 meshes:

**Theta**
``` python
def theta_test_1():
    MeshSegment.DEFAULT_BG_REGION_RATIO = 1.06
    MeshSegment.DEFAULT_FG_REGION_RATIO = 1.02
    mesh = Mesh(0.00, numpy.pi, False)
    mesh.insert_mesh_segment(MeshSegment(1.10, 1.40, 0.01))
    mesh.insert_mesh_segment(MeshSegment(1.30, 1.90, 0.02))
    mesh.insert_mesh_segment(MeshSegment(0.40, 2.80, 0.04))
    if mesh.is_valid():
        adj_mesh = mesh.resolve_mesh_segments().json_dict()
        legacy_mesh = mesh.build_legacy_mesh().json_dict()
        create_psi_mesh(adj_mesh, legacy_mesh, mesh_type="t", dir_name=os.getcwd(),
             output_file_name="tmp_mesh_t.dat", mesh_res_file_name="mesh_res_t.dat",
             save_plot=True, show_plot=False, save_plot_path=os.getcwd(), plot_file_name="t_mesh_spacing.png")
``` 

**Phi**
``` python
def phi_test_1():
    MeshSegment.DEFAULT_BG_REGION_RATIO = 1.06
    mesh = Mesh(0.00, 2 * numpy.pi, True)
    mesh.insert_mesh_segment(MeshSegment(3.0, 3.3, 0.01))
    mesh.insert_mesh_segment(MeshSegment(2.8, 3.8, 0.02))
    mesh.insert_mesh_segment(MeshSegment(0.4, 2 * numpy.pi - 0.3, 0.04))
    if mesh.is_valid():
        adj_mesh = mesh.resolve_mesh_segments().json_dict()
        legacy_mesh = mesh.build_legacy_mesh().json_dict()
        create_psi_mesh(adj_mesh, legacy_mesh, mesh_type="p", dir_name=os.getcwd(),
            output_file_name="tmp_mesh_p.dat", mesh_res_file_name="mesh_res_p.dat",
            save_plot=True, show_plot=False, save_plot_path=os.getcwd(), plot_file_name="p_mesh_spacing.png")
```

**Radial**
``` python
def radial_test_1():
    MeshSegment.DEFAULT_BG_REGION_RATIO = 1.03
    mesh = Mesh(1., 2.5, False)
    mesh.insert_mesh_segment(MeshSegment(1, 1.009, 0.0003, var_ds_ratio=1.02))
    mesh.insert_mesh_segment(MeshSegment(1.0090, 1.009800, 0.00050))
    mesh.insert_mesh_segment(MeshSegment(1.009800, 1.017200, 0.00075))
    mesh.insert_mesh_segment(MeshSegment(1.017200, 1.1000, 0.002))
    mesh.insert_mesh_segment(MeshSegment(1.1000, 1.4000, 0.005))
    mesh.insert_mesh_segment(MeshSegment(1.4000, 2, 0.02))
    if mesh.is_valid():
        adj_mesh = mesh.resolve_mesh_segments().json_dict()
        legacy_mesh = mesh.build_legacy_mesh().json_dict()
        create_psi_mesh(adj_mesh, legacy_mesh, mesh_type="r", dir_name=os.getcwd(),
             output_file_name="tmp_mesh_r.dat", mesh_res_file_name="mesh_res_r.dat",
             save_plot=True, show_plot=False, save_plot_path=os.getcwd(), plot_file_name="r_mesh_spacing.png")
```

Calculate the three meshes above:
``` python
theta_test_1()
phi_test_1()
radial_test_1()
```



Then call `bin/mesh_header_template.py` to write `mesh_header.py` file for MAS. 
``` python
write_mesh_header(r_mesh=True)
``` 

## Option #2
Save the mesh requirements in a json/txt file and then call `MeshGeneratorUI()`.

For example: `ui_session_files/test_2020_06_04_OP1_phi_advance_mesh.json`:

``` python
{
    "lower_bnd_t": 0.0,
    "upper_bnd_t": 3.141592653589793,
    "lower_bnd_p": 0.0,
    "upper_bnd_p": 6.283185307179586,
    "lower_bnd_r": 0.0,
    "upper_bnd_r": 2.5,
    "BG_RATIO": 1.06,
    "FG_RATIO": 1.06,
    "RADIAL_BG_RATIO": 1.06,
    "RADIAL_FG_RATIO": 1.03,
    "box_list": [
        {
            "t0": 0.2,
            "t1": 2.9,
            "p0": 0.0,
            "p1": 6.2831853,
            "r0": 1,
            "r1": 1.09,
            "ds": 0.02,
            "radial_ds": 0.0001,
            "radial_var_ds": null,
            "tp_var_ds": null
        },
        {
            "t0": 0.9252347841897648,
            "t1": 1.724301188717289,
            "p0": 1.4803756547036246,
            "p1": 2.111217553014828,
            "r0": null,
            "r1": null,
            "ds": 0.01,
            "radial_ds": null,
            "radial_var_ds": null,
            "tp_var_ds": null
        },
        {
            "t0": 0.9757021360546608,
            "t1": 1.5476654571901518,
            "p0": 4.693463723435355,
            "p1": 4.9962678346247325,
            "r0": null,
            "r1": null,
            "ds": 0.01,
            "radial_ds": null,
            "radial_var_ds": null,
            "tp_var_ds": null
        },
        {
            "t0": 0.8747674323248681,
            "t1": 1.6654226115415764,
            "p0": 3.0532747878262247,
            "p1": 3.7850513898672213,
            "r0": null,
            "r1": null,
            "ds": 0.001,
            "radial_ds": null,
            "radial_var_ds": null,
            "tp_var_ds": null
        },
        {
            "t0": 1.0934592904060856,
            "t1": 1.2785062472440387,
            "p0": 1.7411236393389222,
            "p1": 2.0102828492850358,
            "r0": null,
            "r1": null,
            "ds": 0.009,
            "radial_ds": null,
            "radial_var_ds": null,
            "tp_var_ds": null
        }
    ]
}
```
Then run:

```python
from mesh_generator import MeshGeneratorUI
MeshGeneratorUI()
```

The resulting `bin/mesh_header.dat` file:
```
&topology 
 nprocs=<NPROC_R>, <NPROC_T>, <NPROC_P> 
 nr=1132
 nt=977
 np=1155
/
&data
 r0=0.0
 r1=2.0
 rfrac=      0.0, 0.4, 0.43600000000000005, 1.0
 drratio=      0.001645715732515603, 1.0, 861.9466194733866
 nfrmesh=5
 tfrac=      0.0, 0.06366197723675814, 0.17084748534747543, 0.2784471218206156,
    0.5301204819277107, 0.5808462620197722, 0.6361402694276503,
    0.9230986699329929, 1.0
 dtratio=      0.6274123713418263, 1.0, 0.05, 1.0, 10.0, 2.0, 1.0,
    1.7908476965428546
 nftmesh=5
 pfrac=      0.0, 0.027313870847428468, 0.0657748065103177, 0.06881320150338566,
    0.11165122024501886, 0.11468961523808682, 0.12771547727313126,
    0.15536248097707034, 0.2026820100709893, 0.2238487246322773,
    0.2776485428688474, 0.39411440632266276, 0.4479142245592328,
    0.4664035629491688, 0.5110457158717358, 0.5386927195756749,
    0.5868854906600123, 0.6144389363158094
 dpratio=      0.4999999999999995, 1.0, 0.8999999999999999, 1.0, 1.1111111111111112,
    1.0, 2.0, 1.0, 1.0, 0.05, 1.0, 20.0, 1.0, 1.0, 0.5, 1.0,
    2.000000000000001, 1.0
 nfpmesh=5
 phishift=1.3087575427128613 
```

## Option #3
**Mesh UI (User Interface)**

The tkinter user interface is an easy way to create 3D meshes by visualizing a magnetogram. 

#  Mesh UI (User Interface)

To start the Mesh generator UI:
```python
from mesh_generator import MeshGeneratorUI
MeshGeneratorUI()
```

Then, if you desire to skip the interative main window then supply:
- Save mesh file directory 
- Previous session json file. 

To open the main window UI, supply:

- Save mesh file directory.
- hdf magnetogram file.
- Previous session json file. (Optional)

![](my-mkdocs/docs/images/ui_main_app.png)

#### The unit tests are found in `test/unit_test.py`.

The tests compare with the dictionary results in in `test/test_results.py`, 
checking both **step #2** (adjust mesh segments) and **step #3** (legacy mesh) of the mesh calculations.
Then will compare with the output.dat file saved in the folder named `output` and test **step #4**
(calling fortran mesh and finding the optimal total number of points in mesh spacing).

- Last update: August 20th, 2020.

- Current tests: 16 Theta, 34 Phi, 5 Radial. (total of 55).

- Note: 
      - All phi cases are periodic.
      - Best way to create a test is as the tests found in `test/unit_test.py`or in the format used in `test/ar_test.py`
      (using 3 different functions). It is important you save the step 2 (adjusted mesh) as 
      a dictionary before computing the legacy mesh. This  dictionary is needed for `check_mesh_valid()` which 
      will check iteratively if the mesh is above user requests.
      - An example test can also be found in `test/create_mesh.py`.

- Observations: Theta tests that have a decreasing first segment will result in a garbage first point in
mesh_res.txt fortran results.








