# Repository Coverage



| Name                                                                        |    Stmts |     Miss |   Cover |   Missing |
|---------------------------------------------------------------------------- | -------: | -------: | ------: | --------: |
| canvodpy/src/canvodpy/\_\_init\_\_.py                                       |       14 |        8 |     43% |     79-96 |
| canvodpy/src/canvodpy/api.py                                                |       71 |       43 |     39% |85-89, 94, 99, 104, 109, 114, 148, 157-159, 162, 211-224, 257-264, 296-301, 334-348, 365, 368, 426-432, 481-486, 510-511 |
| canvodpy/src/canvodpy/globals.py                                            |       50 |        1 |     98% |        15 |
| canvodpy/src/canvodpy/logging/\_\_init\_\_.py                               |        0 |        0 |    100% |           |
| canvodpy/src/canvodpy/logging/context.py                                    |       11 |        3 |     73% | 31-32, 37 |
| canvodpy/src/canvodpy/logging/logging\_config.py                            |       29 |        2 |     93% |     94-95 |
| canvodpy/src/canvodpy/orchestrator/\_\_init\_\_.py                          |       14 |       10 |     29% |     34-43 |
| canvodpy/src/canvodpy/orchestrator/interpolator.py                          |      128 |       92 |     28% |22, 75, 99-152, 162-200, 221-224, 232-289, 302-328, 336, 345-355 |
| canvodpy/src/canvodpy/orchestrator/processor.py                             |      908 |      845 |      7% |92-158, 172-186, 197-220, 230-237, 247-255, 271-295, 309-326, 340-358, 397-417, 431-450, 458-535, 539-550, 584-631, 654-743, 762-967, 983-1174, 1192-1357, 1374-1389, 1421-1532, 1563-1719, 1723-1739, 1762-1856, 1859, 1886, 1889, 1903-1976, 1984-2104, 2118-2299, 2331-2436, 2440-2502 |
| canvodpy/src/canvodpy/research\_sites\_config.py                            |       12 |        2 |     83% |     26-28 |
| canvodpy/src/canvodpy/settings.py                                           |       53 |       21 |     60% |19-21, 112, 126-138, 173-183 |
| canvodpy/tests/test\_integration\_aux\_sid\_filtering.py                    |       47 |       45 |      4% |     12-91 |
| canvodpy/tests/test\_integration\_sid\_filtering.py                         |       46 |       37 |     20% |25-59, 64-74 |
| canvodpy/tests/test\_umbrella\_meta.py                                      |        4 |        0 |    100% |           |
| conftest.py                                                                 |      109 |       65 |     40% |24-29, 35, 41, 47, 53-60, 66-73, 79, 85, 91, 97-103, 109-115, 137-142, 148, 154, 160, 166-173, 179-186, 192-195, 201-204 |
| packages/canvod-aux/src/canvod/aux/\_\_init\_\_.py                          |       26 |        4 |     85% |113-114, 136-137 |
| packages/canvod-aux/src/canvod/aux/\_internal/\_\_init\_\_.py               |        4 |        0 |    100% |           |
| packages/canvod-aux/src/canvod/aux/\_internal/logger.py                     |       36 |        0 |    100% |           |
| packages/canvod-aux/src/canvod/aux/\_internal/units.py                      |        5 |        0 |    100% |           |
| packages/canvod-aux/src/canvod/aux/augmentation.py                          |      205 |      164 |     20% |59-63, 83-86, 96-97, 100, 125-126, 147, 158, 161, 176, 180, 186-213, 228, 232, 257-272, 304-309, 315, 328-329, 357-402, 417-438, 441, 464-480, 502-549, 554-600, 608-612, 667-708, 713-733 |
| packages/canvod-aux/src/canvod/aux/clock/\_\_init\_\_.py                    |        4 |        0 |    100% |           |
| packages/canvod-aux/src/canvod/aux/clock/parser.py                          |       48 |       41 |     15% |39-53, 82-128, 146-153 |
| packages/canvod-aux/src/canvod/aux/clock/reader.py                          |       53 |       32 |     40% |66-69, 73-77, 96-101, 116-144, 161-182, 199-218 |
| packages/canvod-aux/src/canvod/aux/clock/validator.py                       |       32 |       28 |     12% |37-69, 87-103 |
| packages/canvod-aux/src/canvod/aux/container.py                             |       10 |        0 |    100% |           |
| packages/canvod-aux/src/canvod/aux/core/\_\_init\_\_.py                     |        3 |        0 |    100% |           |
| packages/canvod-aux/src/canvod/aux/core/base.py                             |       68 |       34 |     50% |56-64, 98-99, 129-136, 168-170, 181, 186, 191-195, 205-212, 217, 222 |
| packages/canvod-aux/src/canvod/aux/core/downloader.py                       |      136 |      114 |     16% |42, 64-85, 109-162, 168-190, 194-253, 269-300, 304-306, 310-312 |
| packages/canvod-aux/src/canvod/aux/ephemeris/\_\_init\_\_.py                |        4 |        0 |    100% |           |
| packages/canvod-aux/src/canvod/aux/ephemeris/parser.py                      |       79 |       67 |     15% |29-30, 47-133, 153-154, 183-196, 200 |
| packages/canvod-aux/src/canvod/aux/ephemeris/reader.py                      |       83 |       59 |     29% |64-71, 75-79, 88-92, 104-129, 149-166, 170-180, 199-240, 247-254 |
| packages/canvod-aux/src/canvod/aux/ephemeris/validator.py                   |       36 |       26 |     28% |25-27, 43-47, 51-57, 61-67, 71-86, 91 |
| packages/canvod-aux/src/canvod/aux/interpolation/\_\_init\_\_.py            |        2 |        0 |    100% |           |
| packages/canvod-aux/src/canvod/aux/interpolation/interpolator.py            |      129 |       53 |     59% |27, 88, 92, 122, 129-193, 227-243, 298, 355, 360, 380, 413-423 |
| packages/canvod-aux/src/canvod/aux/matching/\_\_init\_\_.py                 |        2 |        0 |    100% |           |
| packages/canvod-aux/src/canvod/aux/matching/dataset\_matcher.py             |       38 |       28 |     26% |97-104, 130-137, 154-155, 176-177, 196-197, 225-258 |
| packages/canvod-aux/src/canvod/aux/pipeline.py                              |      172 |      143 |     17% |71-78, 104-114, 129-163, 194-204, 208, 212, 252-284, 288, 298, 353-412, 416-417, 422-641 |
| packages/canvod-aux/src/canvod/aux/position/\_\_init\_\_.py                 |        3 |        0 |    100% |           |
| packages/canvod-aux/src/canvod/aux/position/position.py                     |       34 |        9 |     74% |    97-109 |
| packages/canvod-aux/src/canvod/aux/position/spherical\_coords.py            |       23 |        0 |    100% |           |
| packages/canvod-aux/src/canvod/aux/preprocessing.py                         |       89 |        7 |     92% |115, 119-123, 130 |
| packages/canvod-aux/src/canvod/aux/products/\_\_init\_\_.py                 |        3 |        0 |    100% |           |
| packages/canvod-aux/src/canvod/aux/products/models.py                       |      103 |       44 |     57% |52-54, 60-63, 108-110, 116-119, 167-176, 192-206, 223-224, 228, 232-247 |
| packages/canvod-aux/src/canvod/aux/products/registry.py                     |       27 |       10 |     63% |332-333, 341-351 |
| packages/canvod-aux/test\_download.py                                       |       24 |       18 |     25% | 12-41, 45 |
| packages/canvod-aux/test\_mwe.py                                            |       65 |       58 |     11% |13-115, 119 |
| packages/canvod-aux/tests/conftest.py                                       |       62 |        1 |     98% |        24 |
| packages/canvod-aux/tests/test\_aux\_meta.py                                |       59 |        4 |     93% |16-17, 25-26 |
| packages/canvod-aux/tests/test\_container.py                                |       61 |        0 |    100% |           |
| packages/canvod-aux/tests/test\_internal\_date\_utils.py                    |       90 |        0 |    100% |           |
| packages/canvod-aux/tests/test\_internal\_logger.py                         |       47 |        0 |    100% |           |
| packages/canvod-aux/tests/test\_internal\_units.py                          |       31 |        0 |    100% |           |
| packages/canvod-aux/tests/test\_interpolation.py                            |      168 |        0 |    100% |           |
| packages/canvod-aux/tests/test\_pint\_warnings.py                           |       37 |       23 |     38% |24-27, 34-46, 49-65 |
| packages/canvod-aux/tests/test\_position.py                                 |      174 |        0 |    100% |           |
| packages/canvod-aux/tests/test\_position\_properties.py                     |      152 |        1 |     99% |       488 |
| packages/canvod-aux/tests/test\_preprocessing.py                            |      191 |        0 |    100% |           |
| packages/canvod-aux/tests/test\_products.py                                 |      112 |        2 |     98% |   203-204 |
| packages/canvod-grids/src/canvod/grids/\_\_init\_\_.py                      |       26 |        2 |     92% |  179, 184 |
| packages/canvod-grids/src/canvod/grids/aggregation.py                       |      194 |      167 |     14% |78-116, 150-164, 226-335, 358-369, 395-403, 420, 437, 451, 462, 478-482, 490-502, 511-528, 540-595, 607-619, 636-653 |
| packages/canvod-grids/src/canvod/grids/core/\_\_init\_\_.py                 |        4 |        0 |    100% |           |
| packages/canvod-grids/src/canvod/grids/core/grid\_builder.py                |       34 |        1 |     97% |        99 |
| packages/canvod-grids/src/canvod/grids/core/grid\_data.py                   |      118 |       58 |     51% |82, 86-94, 98, 106, 140-164, 168-207, 239-248 |
| packages/canvod-grids/src/canvod/grids/core/grid\_types.py                  |        9 |        0 |    100% |           |
| packages/canvod-grids/src/canvod/grids/grids\_impl/\_\_init\_\_.py          |        8 |        0 |    100% |           |
| packages/canvod-grids/src/canvod/grids/grids\_impl/equal\_angle\_grid.py    |       33 |        0 |    100% |           |
| packages/canvod-grids/src/canvod/grids/grids\_impl/equal\_area\_grid.py     |       43 |        2 |     95% |  141, 176 |
| packages/canvod-grids/src/canvod/grids/grids\_impl/equirectangular\_grid.py |       22 |        0 |    100% |           |
| packages/canvod-grids/src/canvod/grids/grids\_impl/fibonacci\_grid.py       |       61 |       51 |     16% |123-132, 143, 170-250, 267-283 |
| packages/canvod-grids/src/canvod/grids/grids\_impl/geodesic\_grid.py        |      100 |        2 |     98% |  141, 225 |
| packages/canvod-grids/src/canvod/grids/grids\_impl/healpix\_grid.py         |       46 |       37 |     20% |117-141, 156, 181-235, 248 |
| packages/canvod-grids/src/canvod/grids/grids\_impl/htm\_grid.py             |       74 |        0 |    100% |           |
| packages/canvod-grids/src/canvod/grids/operations.py                        |      280 |      105 |     62% |152-184, 212-265, 302, 359-366, 372-392, 398-405, 468, 473-518, 660 |
| packages/canvod-grids/src/canvod/grids/workflows/\_\_init\_\_.py            |        2 |        0 |    100% |           |
| packages/canvod-grids/src/canvod/grids/workflows/adapted\_workflow.py       |      187 |      163 |     13% |45-52, 71-73, 105-106, 132-136, 173-222, 272, 329-381, 417-482, 490-501, 510-523, 538-558, 611-685, 706, 725-753 |
| packages/canvod-grids/tests/test\_cell\_assignment.py                       |       86 |        8 |     91% |   130-152 |
| packages/canvod-grids/tests/test\_equal\_area\_grid.py                      |      132 |        0 |    100% |           |
| packages/canvod-grids/tests/test\_grid\_operations.py                       |      109 |        0 |    100% |           |
| packages/canvod-grids/tests/test\_grid\_properties.py                       |      109 |        5 |     95% |   100-110 |
| packages/canvod-grids/tests/test\_grids.py                                  |      146 |        1 |     99% |       266 |
| packages/canvod-grids/tests/test\_grids\_meta.py                            |        3 |        0 |    100% |           |
| packages/canvod-readers/src/canvod/readers/\_\_init\_\_.py                  |        6 |        0 |    100% |           |
| packages/canvod-readers/src/canvod/readers/base.py                          |      126 |       72 |     43% |49-53, 68-101, 122-140, 156-166, 186-189, 312-313, 377, 424-425, 454-471, 489-509, 521 |
| packages/canvod-readers/src/canvod/readers/gnss\_specs/\_\_init\_\_.py      |        0 |        0 |    100% |           |
| packages/canvod-readers/src/canvod/readers/gnss\_specs/bands.py             |      126 |       97 |     23% |171-427, 431-437 |
| packages/canvod-readers/src/canvod/readers/gnss\_specs/constants.py         |       19 |        1 |     95% |        25 |
| packages/canvod-readers/src/canvod/readers/gnss\_specs/constellations.py    |      274 |      113 |     59% |85-87, 103-115, 131-142, 177-260, 265, 352-355, 486-492, 679-685, 786-787, 888-894, 907-917, 976-982, 1045-1051, 1126-1132, 1137-1178 |
| packages/canvod-readers/src/canvod/readers/gnss\_specs/exceptions.py        |       19 |        3 |     84% |54, 100, 162 |
| packages/canvod-readers/src/canvod/readers/gnss\_specs/metadata.py          |       10 |        0 |    100% |           |
| packages/canvod-readers/src/canvod/readers/gnss\_specs/models.py            |      289 |      165 |     43% |91-92, 96-97, 130-136, 159-163, 246, 266, 300, 316, 332, 353-359, 440, 474-477, 517-525, 551-560, 582-605, 650-684, 715-732, 748, 785-818, 868-918, 940-970, 987-996, 1019, 1034-1045, 1088-1104, 1121-1138 |
| packages/canvod-readers/src/canvod/readers/gnss\_specs/signals.py           |       46 |        1 |     98% |       142 |
| packages/canvod-readers/src/canvod/readers/gnss\_specs/utils.py             |       24 |        1 |     96% |        10 |
| packages/canvod-readers/src/canvod/readers/matching/\_\_init\_\_.py         |        3 |        0 |    100% |           |
| packages/canvod-readers/src/canvod/readers/matching/dir\_matcher.py         |       93 |       73 |     22% |64-71, 82-83, 102-110, 129-145, 163, 181-183, 243-249, 265-273, 291-297, 308-340, 351-373 |
| packages/canvod-readers/src/canvod/readers/matching/models.py               |        7 |        0 |    100% |           |
| packages/canvod-readers/src/canvod/readers/rinex/\_\_init\_\_.py            |        2 |        0 |    100% |           |
| packages/canvod-readers/src/canvod/readers/rinex/v3\_04.py                  |      644 |      509 |     21% |150-155, 163-173, 195-338, 348-379, 396-401, 420-429, 446-453, 472-503, 522-530, 549-562, 581-611, 630-639, 644, 648, 654-655, 722-743, 755, 759, 766, 777-785, 797, 809, 821-826, 838-840, 852, 864-868, 887-892, 915-990, 998-1042, 1054, 1070-1082, 1109-1112, 1131, 1158-1169, 1176-1190, 1201-1216, 1235-1258, 1287-1314, 1340-1356, 1370-1613, 1651-1684, 1723-1750, 1753-1758, 1761-1828, 1843-1844, 1946-1987 |
| packages/canvod-readers/tests/conftest.py                                   |       19 |        8 |     58% |21, 27-30, 36-38 |
| packages/canvod-readers/tests/test\_gnss\_specs\_base.py                    |      101 |        2 |     98% |   167-168 |
| packages/canvod-readers/tests/test\_readers\_meta.py                        |       38 |        0 |    100% |           |
| packages/canvod-readers/tests/test\_rinex\_integration.py                   |      168 |      108 |     36% |20, 28-37, 41-45, 49-64, 68-96, 100-120, 125-134, 138-152, 157-172, 176-192, 196-211, 215-220, 224-230, 235-247 |
| packages/canvod-readers/tests/test\_rinex\_v3.py                            |      139 |       98 |     29% |19, 27-32, 36-43, 47-55, 59-65, 73-77, 81-84, 88-98, 102-108, 112-118, 122-129, 133-140, 144-151, 155-161, 165-171, 175-181, 189-200, 204-215, 238-242 |
| packages/canvod-readers/tests/test\_signal\_mapping.py                      |      250 |        6 |     98% |433-436, 441-444 |
| packages/canvod-store/src/canvod/store/\_\_init\_\_.py                      |        5 |        0 |    100% |           |
| packages/canvod-store/src/canvod/store/manager.py                           |      217 |      179 |     18% |69-89, 98, 103, 112, 117, 147-156, 174-197, 208, 219, 242-254, 281-304, 327-338, 365-382, 412-433, 462-495, 517-552, 563-631, 655-709, 719, 729-731, 750, 756-758 |
| packages/canvod-store/src/canvod/store/reader.py                            |      312 |      278 |     11% |45-67, 90-113, 160-182, 188-191, 195-198, 214, 221-224, 228-231, 245-415, 439-610, 614-617, 622-634, 643-665, 676-685, 695-696, 705-787 |
| packages/canvod-store/src/canvod/store/store.py                             |      907 |      765 |     16% |123-128, 149-152, 174, 243-247, 267, 311, 326-354, 380-406, 426-436, 462-487, 521-580, 585-601, 629-645, 654-687, 710-743, 768-815, 830-874, 908-931, 947, 958-981, 993-1041, 1072-1148, 1172-1256, 1273-1289, 1306-1319, 1360-1395, 1401-1412, 1432-1484, 1513-1544, 1564-1577, 1585-1587, 1610-1623, 1659-1714, 1749-1906, 1921-1926, 1931, 1935-1936, 1959-2200, 2218-2238, 2242-2246, 2263-2286, 2305-2311, 2347-2377, 2408-2522, 2539-2569, 2603-2636, 2670-2700, 2746-2765, 2770-2791 |
| packages/canvod-store/src/canvod/store/viewer.py                            |      126 |      100 |     21% |33-40, 61, 69, 371-383, 389-409, 428-483, 487-525, 536-624, 661-662, 671-676, 685, 726-738, 755-757 |
| packages/canvod-store/tests/test\_grid\_storage.py                          |      155 |        0 |    100% |           |
| packages/canvod-store/tests/test\_store\_basic.py                           |       10 |        0 |    100% |           |
| packages/canvod-store/tests/test\_store\_crud.py                            |      126 |        0 |    100% |           |
| packages/canvod-store/tests/test\_store\_integrity.py                       |      158 |        0 |    100% |           |
| packages/canvod-utils/src/canvod/utils/\_\_init\_\_.py                      |        2 |        0 |    100% |           |
| packages/canvod-utils/src/canvod/utils/\_meta.py                            |        5 |        0 |    100% |           |
| packages/canvod-utils/src/canvod/utils/config/\_\_init\_\_.py               |        3 |        0 |    100% |           |
| packages/canvod-utils/src/canvod/utils/config/loader.py                     |       83 |       66 |     20% |32-54, 76-85, 104-119, 124-135, 145-154, 158-165, 181-182, 204-214, 228-233, 260-261 |
| packages/canvod-utils/src/canvod/utils/config/models.py                     |      135 |       41 |     70% |50-61, 100, 104-108, 269-287, 302, 317, 386, 412-415, 460-464, 474-479, 491, 523, 534 |
| packages/canvod-utils/src/canvod/utils/tools/\_\_init\_\_.py                |        6 |        0 |    100% |           |
| packages/canvod-utils/src/canvod/utils/tools/date\_utils.py                 |       96 |       14 |     85% |37, 44, 122, 134, 150, 167, 205, 222, 242, 283-284, 326, 381-382 |
| packages/canvod-utils/src/canvod/utils/tools/hashing.py                     |        9 |        6 |     33% |     32-37 |
| packages/canvod-utils/src/canvod/utils/tools/validation.py                  |        7 |        5 |     29% |     29-33 |
| packages/canvod-utils/src/canvod/utils/tools/version.py                     |       16 |       13 |     19% |     28-45 |
| packages/canvod-utils/tests/test\_config.py                                 |       35 |        8 |     77% |23-25, 53-58 |
| packages/canvod-utils/tests/test\_config\_from\_anywhere.py                 |       56 |       38 |     32% |18, 43-76, 83-116 |
| packages/canvod-utils/tests/test\_configuration.py                          |      164 |       59 |     64% |58, 60, 83, 104, 108, 128-129, 161-182, 208-210, 215-249, 253 |
| packages/canvod-viz/src/canvod/viz/\_\_init\_\_.py                          |        6 |        0 |    100% |           |
| packages/canvod-viz/src/canvod/viz/hemisphere\_2d.py                        |      233 |      151 |     35% |106-107, 117, 186, 192-201, 225, 246-288, 292-366, 371, 376, 441, 487-488, 539-663 |
| packages/canvod-viz/src/canvod/viz/hemisphere\_3d.py                        |      174 |      112 |     36% |126-130, 182, 213-214, 240-275, 299-321, 427-520, 551-594, 623-688, 746-757 |
| packages/canvod-viz/src/canvod/viz/styles.py                                |       49 |        0 |    100% |           |
| packages/canvod-viz/src/canvod/viz/visualizer.py                            |       52 |        3 |     94% |251, 367-368 |
| packages/canvod-viz/tests/test\_integration.py                              |      235 |        1 |     99% |       485 |
| packages/canvod-viz/tests/test\_viz.py                                      |       88 |        0 |    100% |           |
| packages/canvod-viz/tests/test\_viz\_meta.py                                |       32 |        0 |    100% |           |
| packages/canvod-vod/src/canvod/vod/\_\_init\_\_.py                          |        3 |        0 |    100% |           |
| packages/canvod-vod/src/canvod/vod/calculator.py                            |       54 |       14 |     74% |45, 59, 92-106, 196-198 |
| packages/canvod-vod/tests/test\_vod\_basic.py                               |        8 |        0 |    100% |           |
| packages/canvod-vod/tests/test\_vod\_calculator.py                          |      113 |        1 |     99% |       298 |
| packages/canvod-vod/tests/test\_vod\_meta.py                                |        3 |        0 |    100% |           |
| packages/canvod-vod/tests/test\_vod\_properties.py                          |      138 |        9 |     93% |28, 37, 46, 185, 237, 301, 470, 473, 485 |
| **TOTAL**                                                                   | **12276** | **5866** | **52%** |           |


## Setup coverage badge

Below are examples of the badges you can use in your main branch `README` file.

### Direct image

[![Coverage badge](https://github.com/nfb2021/canvodpy/raw/python-coverage-comment-action-data/badge.svg)](https://github.com/nfb2021/canvodpy/tree/python-coverage-comment-action-data)

This is the one to use if your repository is private or if you don't want to customize anything.



## What is that?

This branch is part of the
[python-coverage-comment-action](https://github.com/marketplace/actions/python-coverage-comment)
GitHub Action. All the files in this branch are automatically generated and may be
overwritten at any moment.