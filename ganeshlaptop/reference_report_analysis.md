# Analysis of supplied reference PDFs and tutorial material

**Source analyzed:** *Deep Learning on Point Clouds, Voxel Grids and Meshes*, Report 3, 25 pages, supplied as `23BDS004 Report.pdf`. The source PDF metadata identifies its author as Aggimalla Abhishek (23BDS004). Its benchmark figures are cited as **reference-reported**, not represented as experiments run by J GANESH KUMAR REDDY.

## Page-by-page audit

| Source page | Information reviewed and carried into the synthesis |
|---|---|
| 1 | Report scope, course, three representations, ModelNet40/10 and SHREC'16, PointNet++/VoxelCNN/MeshCNN, software and submission context. |
| 2 | Abstract and headline results: PointNet++ 88.1% instance / 82.7% class after 15 epochs; VoxelCNN 90.1% / 89.8% after 15 epochs; MeshCNN peak 85.0%, late-run 82.4%; Chamfer-based conversion evaluation. |
| 3 | Contents and source-code appendix map; used to ensure the code appendix, logs, patches and conversion work were considered, not only the main narrative. |
| 4 | 3D representation motivation, objectives, five practicals including 7.1 synthetic-cloud I/O, PointNet permutation invariance, SSG sampling/grouping and local-feature hierarchy. |
| 5 | Voxel memory scaling and dense-CNN trade-offs; MeshCNN edge neighborhoods and five features; dataset splits and formats for ModelNet40, ModelNet10 and SHREC'16. |
| 6 | Reference machine/software, MPS/CPU division, device-port and NumPy compatibility patches, zip-streamed ModelNet40 cache preparation, model sizes, optimizer, LR schedule, batch sizes, augmentation, epoch limits and reported runtime. |
| 7 | Synthetic sphere setup (3,000 points, Gaussian noise sigma 0.01, radius mean 0.9998 / standard deviation 0.0099); PointNet++ curve interpretation and best checkpoint/test-vote results. |
| 8 | PointNet++ comparison with paper/repository references; the tutorial voxelizer's non-cubic-grid bug and shape mismatch; corrected padding approach; ModelNet10 voxel training results and confusion themes. |
| 9 | VoxelCNN curves and confusion matrix; SHREC'16 MeshCNN setup, 20 augmentations, 750-to-180 edge pooling schedule, peak and late-epoch behavior. |
| 10 | MeshCNN training curve interpretation; complete chair conversion protocol, oriented-normal requirement, Poisson/Ball-Pivoting settings, Chamfer definition, metric table and open-mesh caveat. |
| 11 | Five-way visualization of a ModelNet10 chair; classifier summary (parameters, epochs, time per epoch/shape, accuracy and published reference); cautions against cross-dataset accuracy ranking. |
| 12 | Limitations (short schedules, one seed, test-split model selection, one-shape conversion study), final conclusions and bibliography. |
| 13 | Terminal evidence for synthetic point-cloud and voxel demos plus PointNet++ per-epoch training log excerpts. |
| 14 | ModelNet10 voxelization/training terminal output, per-class accuracies, and late-epoch MeshCNN test accuracy logs. |
| 15 | Conversion terminal output, mesh topology, point/voxel counts, reconstruction mesh sizes and Chamfer values. |
| 16 | Reproduction commands, synthetic-sphere implementation, and the original tutorial voxelization function with its correction. |
| 17 | VoxelCNN architecture/forward pass and the beginning of a multiprocessing ModelNet10 voxel-cache builder. |
| 18 | Completion of the cache builder and the VoxelCNN training/evaluation script setup. |
| 19 | VoxelCNN training loop, augmentations, metrics, checkpointing and confusion-matrix reporting. |
| 20 | Open3D Poisson and Ball-Pivoting conversions, face-derived normals, occupied-voxel centers, symmetric Chamfer implementation and visualization. |
| 21 | Conversion-figure layout and the ModelNet40 zip-streaming cache-preparation script (1,024 points per shape). |
| 22 | Log parsing and the general figure-generation/report-data pipeline. |
| 23 | PointNet++/MeshCNN/VoxelCNN curve and per-class chart construction. |
| 24 | PointNet++ patch that replaces hard-coded CUDA placement with runtime device placement and maps checkpoints to the chosen device. |
| 25 | Continuation of the PointNet++ device/test-loader patch and the MeshCNN NumPy 1.24+ ragged-array cache workaround. |

## User-provided tutorial excerpt

In addition to the 25-page PDF, the supplied Sections 7.2–7.5 tutorial text was incorporated in the revised report's tutorial-workflow appendix. This includes the legacy PointNet++ conda/CUDA setup, ModelNet40 download and directory layout, 200-epoch command and flags (`--use_normals`, `--use_uniform_sample`, SSG vs MSG); voxel-demo dependencies, 32³ CNN shape and non-cubic-grid bug warning; ModelNet10 `.off` workflow and cubic memory scaling; MeshCNN environment/data/train/test/view commands; and the four representation-conversion routes with a 4,096-point sampling example. These commands are marked as tutorial guidance, not as locally executed evidence.

## Second supplied report: 23BCS071

**Source analyzed:** *3D Shape Understanding and Recognition Using Deep Learning: Point Clouds, Volumetric Representations, and Mesh-Based Learning*, Assignment 3, 11-page PDF supplied as `23BCS071_Assignmnet-3_report.pdf`. The title page identifies Anjan Kothapally (23BCS071). Its reported measurements are cited separately as **source-reported**; the PDF is not treated as work executed by J GANESH KUMAR REDDY.

| Source page | Information reviewed and carried into the synthesis |
|---|---|
| 1 | Assignment scope, claimed ModelNet40/10 and SHREC coverage, PointNet++/VoxNet/MeshCNN, and conversion pipeline; cover identifies the source report's student. |
| 2 | Conceptual comparison of point sets, cubic voxel memory scaling and irregular mesh topology. |
| 3 | PointNet++ FPS, ball-query and local PointNet explanation; ModelNet40 count of 12,311 and seven HDF5-shard description. |
| 4 | Voxel CNN and MeshCNN explanation, including the source's listed five edge features and pooling description. |
| 5 | Mesh-to-point, mesh-to-voxel, voxel-center and screened-Poisson pipeline; source-reported mesh output of 11,818 vertices / 23,233 faces. |
| 6 | Colab-style environment claim (PyTorch 2.6.0+cu124, CUDA available), seven HDF5 shard sizes and a displayed HDF5 conversion helper. Although the text says the shards were downloaded from Hugging Face, the shown cell only lists/stats local paths; the printed helper assigns train/test counts as constants (9,840 / 2,468) and does not demonstrate parsing/conversion. |
| 7 | Five-epoch PointNet++ SSG, batch size 16 and 3-vote evaluation; source reports 80.5663% instance / 74.3880% class accuracy and separately 82.7184% instance accuracy for a pre-trained checkpoint. |
| 8 | ModelNet10 `.off` loading and a bathtub example; 32³ grid with 8,181 active cells (24.97%); pad/crop helper is referenced but not defined on the page. |
| 9 | Cached 3D-CNN dataset and a different VoxNet-style architecture; source prints 9,798 meshes / 7,982 train / 1,816 test and 100% test accuracy from epoch 1 through 3. It prints epoch-1 train loss 1.0311 / train accuracy 86.67% / test loss 2.90e-6, then near-zero or zero losses and 100% accuracies at epochs 2–3. |
| 10 | MeshCNN repository/environment inspection and edge-operator initialization; `RUN_MESHCNN_TRAINING = False`, so the source explicitly skips SHREC training. |
| 11 | Bathtub conversion outputs: 4,096 sampled points, 8,181 voxel centers, Poisson mesh 11,818 vertices / 23,233 faces, estimated normals (radius 0.1, max_nn 30), and file-existence/size checks. Reported artifact sizes are 292 B (evaluation text), 124,414 B (sampled points), 131,200 B (voxel array), 220,887 B (voxel centers) and 905,071 B (Poisson PLY). No conversion Chamfer score is reported. |

### Cross-report validation notes

- **ModelNet10 count conflict:** [9] records the conventional 4,899 total (3,991 train / 908 test), while [11] prints 9,798 (7,982 / 1,816), exactly twice those counts. The [11] PDF does not explain the doubling or show a duplicate-detection audit. Its count and 100% result therefore remain unverified; the final report flags this rather than treating it as a validated benchmark.
- **ModelNet40 count discrepancy:** [11] says 12,311 shapes, but its printed helper returns 9,840 train + 2,468 test = 12,308. The standard split recorded in [9] is 9,843 + 2,468 = 12,311. The shown helper assigns constants rather than demonstrating HDF5 parsing, leaving three training shapes unexplained in the excerpt.
- **Perfect VoxelCNN score:** [11] prints 100% test accuracy and zero/near-zero loss after two to three epochs. That is an extraordinary result and the provided pages do not show enough code to establish split independence, label correctness or leakage checks. It is quoted only as a source claim and excluded from trusted comparison charts pending validation.
- **MeshCNN scope:** [11] confirms the environment and scripts but explicitly sets training to false. It reports no SHREC test accuracy; this differs from the trained 100-epoch SHREC result reported in [9].
- **Verification scope:** [11]'s final snippet checks path existence and file sizes; this does not prove checkpoint quality, content correctness or benchmark validity. Its Poisson reconstruction also uses estimated normals and reports mesh counts, not a Chamfer comparison.
- **Architecture and data provenance differ:** [11]'s 3D CNN includes a stride-2 convolution and batch normalization and is not identical to the simpler CNN in [9]. Its Colab CUDA environment is distinct from both the Apple-MPS environment in [9] and the CPU-only local workspace.

## Synthesis rule

The final report keeps three evidence tracks separate:

1. **Local execution in this workspace:** CPU smoke tests on generated fixtures, captured in `outputs/logs/` and `outputs/screenshots/`; no local ModelNet or SHREC benchmark claim.
2. **Supplied report [9]:** Apple-M4/MPS and CPU benchmark results and conversion measurements, attributed to its author and not independently rerun here.
3. **Supplied report [11]:** Colab/ CUDA claims and notebook outputs attributed to its author; conflicting counts, perfect VoxelCNN scores, and skipped MeshCNN training are clearly qualified.

The original tutorial excerpt is separately identified as [10]. This attribution allows methodological ideas and results from both reports to inform the synthesis without passing either student's outcomes off as local experiments.
