<h1 align='center'>ISAT_with_segment_anything</h1>
<h2 align='center'>An Interactive Semi-Automatic Annotation Tool Based on Segment Anything</h2>
<p align='center'>
    <a href='https://github.com/yatengLG/ISAT_with_segment_anything' target="_blank"><img alt="GitHub forks" src="https://img.shields.io/github/stars/yatengLG/ISAT_with_segment_anything"></a>
    <a href='https://github.com/yatengLG/ISAT_with_segment_anything' target="_blank"><img alt="GitHub forks" src="https://img.shields.io/github/forks/yatengLG/ISAT_with_segment_anything"></a>
    <a href='https://pypi.org/project/isat-sam/' target="_blank"><img alt="PyPI - Version" src="https://img.shields.io/pypi/v/isat-sam"></a>
    <a href='https://pypi.org/project/isat-sam/' target="_blank"><img alt="Pepy Total Downlods" src="https://img.shields.io/pepy/dt/isat-sam"></a>
</p>
<p align='center'>
    <a href='README-cn.md'><b>[中文]</b></a>
    <a href='README.md'><b>[English]</b></a>
</p>
<p align='center'><img src="./display/标注.gif" alt="标注.gif"></p>

Our tool enables interactive use of [segment anything](https://github.com/facebookresearch/segment-anything) for rapid image segmentation with low RAM requirements (optional bf16 mode).

Demo Video：[YouTube](https://www.youtube.com/watch?v=yLdZCPmX-Bc)

---

# Features and Installation
- &#x1F389;: **In version 1.4.0, ISAT add a plugin system.** You can use a small amount of code to extend the functionality of ISAT.
  
    Here are some official plugin examples:
  - [ISAT_plugin_mask_export](https://github.com/yatengLG/ISAT_plugin_mask_export): An auto-annotation function based on the YOLO object detection model, implemented with just 240 lines of code.
  - [ISAT_plugin_auto_annotate](https://github.com/yatengLG/ISAT_plugin_auto_annotate): A mask export function, implemented with just 160 lines of code.

## Install
- Create a conda environment(recommended, optional)
```shell
# create environment
conda create -n isat_env python=3.8

# activate environment
conda activate isat_env
```

- Install
```shell
pip install isat-sam
```

- Run
```shell
isat-sam
```

# Star History

**Please support us with a star—it's like a virtual coffee!**
[![Star History Chart](https://api.star-history.com/svg?repos=yatengLG/ISAT_with_segment_anything&type=Date)](https://star-history.com/#yatengLG/ISAT_with_segment_anything&Date)


# Contributors

<table border="0">
<tr>
    <td><img alt="yatengLG" src="https://avatars.githubusercontent.com/u/31759824?v=4" width="60" height="60" href="">
    <td><img alt="Alias-z" src="https://avatars.githubusercontent.com/u/66273343?v=4" width="60" height="60" href="">
    <td>...
</td>
</tr>
<tr>
  <td><a href="https://github.com/yatengLG">yatengLG</a>
  <td><a href="https://github.com/Alias-z">Alias-z</a>
    <td><a href="https://github.com/yatengLG/ISAT_with_segment_anything/graphs/contributors">...</a>
</tr>
</table>


# Citation
```text
@misc{ISAT_with_segment_anything,
  title={{ISAT with Segment Anything: An Interactive Semi-Automatic Annotation Tool}},
  author={Ji, Shuwei and Zhang, Hongyuan},
  url={https://github.com/yatengLG/ISAT_with_segment_anything},
  note={Updated on 2025-02-07},
  year={2024},
  version={1.33}
}
```
