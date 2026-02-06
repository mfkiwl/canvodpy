# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/nfb2021/canvodpy/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                                                         |    Stmts |     Miss |   Cover |   Missing |
|----------------------------------------------------------------------------- | -------: | -------: | ------: | --------: |
| canvodpy/src/canvodpy/\_\_init\_\_.py                                        |       41 |        6 |     85% |216-217, 223-224, 230-231 |
| canvodpy/src/canvodpy/api.py                                                 |       85 |       53 |     38% |89, 94, 99, 104, 109, 114, 148, 157-159, 162, 214-238, 272-289, 321-326, 358-391, 408, 411, 469-475, 524-529, 553-554 |
| canvodpy/src/canvodpy/factories.py                                           |       56 |        0 |    100% |           |
| canvodpy/src/canvodpy/functional.py                                          |       69 |       49 |     29% |88-98, 182-192, 243-255, 306-317, 358-373, 414-438, 498-518 |
| canvodpy/src/canvodpy/globals.py                                             |       50 |        0 |    100% |           |
| canvodpy/src/canvodpy/logging/\_\_init\_\_.py                                |        6 |        0 |    100% |           |
| canvodpy/src/canvodpy/logging/logging\_config.py                             |      140 |        9 |     94% |68, 114, 125-126, 128, 151, 196, 423-424 |
| canvodpy/src/canvodpy/orchestrator/\_\_init\_\_.py                           |       14 |       10 |     29% |     34-46 |
| canvodpy/src/canvodpy/orchestrator/interpolator.py                           |      128 |       92 |     28% |22, 75, 99-156, 166-203, 224-226, 234-303, 316-340, 348, 357-367 |
| canvodpy/src/canvodpy/orchestrator/processor.py                              |     1014 |      950 |      6% |92-242, 256-270, 280-303, 313-320, 330-338, 354-378, 392-409, 423-441, 480-506, 517-548, 556-689, 693-704, 730-784, 818-911, 934-1192, 1216-1414, 1430-1663, 1681-1847, 1863-1878, 1910-2023, 2054-2207, 2215-2231, 2254-2354, 2357, 2386, 2389, 2405-2481, 2489-2604, 2618-2802, 2834-2941, 2945-3012 |
| canvodpy/src/canvodpy/research\_sites\_config.py                             |       12 |        2 |     83% |     27-29 |
| canvodpy/src/canvodpy/settings.py                                            |       53 |       21 |     60% |20-22, 113, 127-138, 173-184 |
| canvodpy/src/canvodpy/workflow.py                                            |       90 |       71 |     21% |126-139, 190-223, 277-314, 338-360, 383-395, 417-428, 451-457, 461 |
| canvodpy/tests/test\_backward\_compatibility.py                              |      136 |       12 |     91% |25, 35-36, 46, 66-67, 77, 87-88, 137-139, 152 |
| canvodpy/tests/test\_factory\_validation.py                                  |       77 |        3 |     96% |88, 91, 142 |
| canvodpy/tests/test\_integration\_aux\_sid\_filtering.py                     |       45 |       43 |      4% |     13-93 |
| canvodpy/tests/test\_integration\_sid\_filtering.py                          |       45 |       37 |     18% |23-58, 63-75 |
| canvodpy/tests/test\_umbrella\_meta.py                                       |        4 |        0 |    100% |           |
| canvodpy/tests/test\_workflow\_integration.py                                |      117 |       29 |     75% |21, 31-32, 40-42, 55, 67-69, 81, 90-91, 103-104, 114, 126-130, 143-144, 169-173, 187-191 |
| conftest.py                                                                  |      109 |       65 |     40% |25-30, 36, 42, 48, 54-65, 71-82, 88, 94, 100, 106-112, 118-124, 146-150, 156, 162, 168, 174-185, 191-202, 208-211, 217-220 |
| packages/canvod-auxiliary/src/canvod/auxiliary/\_\_init\_\_.py               |       26 |        4 |     85% |113-114, 136-137 |
| packages/canvod-auxiliary/src/canvod/auxiliary/\_internal/\_\_init\_\_.py    |        4 |        0 |    100% |           |
| packages/canvod-auxiliary/src/canvod/auxiliary/\_internal/logger.py          |        5 |        0 |    100% |           |
| packages/canvod-auxiliary/src/canvod/auxiliary/\_internal/units.py           |        5 |        1 |     80% |        16 |
| packages/canvod-auxiliary/src/canvod/auxiliary/augmentation.py               |      205 |      164 |     20% |61-65, 85-90, 100-101, 104, 131-132, 157, 168, 171, 186, 190, 200-226, 241, 245, 274-292, 324-329, 336, 349-350, 380-427, 442-462, 465, 488-506, 528-580, 585-633, 641-645, 700-745, 750-770 |
| packages/canvod-auxiliary/src/canvod/auxiliary/clock/\_\_init\_\_.py         |        4 |        0 |    100% |           |
| packages/canvod-auxiliary/src/canvod/auxiliary/clock/parser.py               |       48 |       41 |     15% |39-53, 82-128, 146-153 |
| packages/canvod-auxiliary/src/canvod/auxiliary/clock/reader.py               |       53 |       32 |     40% |67-70, 74-78, 97-102, 117-145, 162-183, 200-219 |
| packages/canvod-auxiliary/src/canvod/auxiliary/clock/validator.py            |       32 |       28 |     12% |37-69, 87-101 |
| packages/canvod-auxiliary/src/canvod/auxiliary/container.py                  |       10 |        0 |    100% |           |
| packages/canvod-auxiliary/src/canvod/auxiliary/core/\_\_init\_\_.py          |        3 |        0 |    100% |           |
| packages/canvod-auxiliary/src/canvod/auxiliary/core/base.py                  |       68 |       34 |     50% |57-65, 99-100, 130-137, 169-171, 182, 187, 192-196, 206-213, 218, 223 |
| packages/canvod-auxiliary/src/canvod/auxiliary/core/downloader.py            |      150 |      126 |     16% |46, 68-87, 111-214, 220-242, 246-303, 319-350, 354-356, 360-362 |
| packages/canvod-auxiliary/src/canvod/auxiliary/ephemeris/\_\_init\_\_.py     |        4 |        0 |    100% |           |
| packages/canvod-auxiliary/src/canvod/auxiliary/ephemeris/parser.py           |       79 |       67 |     15% |29-30, 47-135, 155-156, 185-198, 202 |
| packages/canvod-auxiliary/src/canvod/auxiliary/ephemeris/reader.py           |       83 |       59 |     29% |64-71, 75-79, 88-92, 104-128, 148-165, 169-179, 198-239, 246-253 |
| packages/canvod-auxiliary/src/canvod/auxiliary/ephemeris/validator.py        |       36 |       26 |     28% |25-27, 43-47, 51-55, 59-63, 67-82, 88 |
| packages/canvod-auxiliary/src/canvod/auxiliary/interpolation/\_\_init\_\_.py |        2 |        0 |    100% |           |
| packages/canvod-auxiliary/src/canvod/auxiliary/interpolation/interpolator.py |      129 |       53 |     59% |27, 90, 94, 123, 131-197, 231-247, 304, 366, 371, 391, 423-433 |
| packages/canvod-auxiliary/src/canvod/auxiliary/matching/\_\_init\_\_.py      |        2 |        0 |    100% |           |
| packages/canvod-auxiliary/src/canvod/auxiliary/matching/dataset\_matcher.py  |       38 |       28 |     26% |95-102, 128-135, 152-153, 172-173, 192-193, 221-250 |
| packages/canvod-auxiliary/src/canvod/auxiliary/pipeline.py                   |      183 |      154 |     16% |71-81, 105-119, 139-209, 244-256, 260, 264, 304-337, 341, 351, 406-465, 469-470, 477-702 |
| packages/canvod-auxiliary/src/canvod/auxiliary/position/\_\_init\_\_.py      |        3 |        0 |    100% |           |
| packages/canvod-auxiliary/src/canvod/auxiliary/position/position.py          |       34 |        9 |     74% |    97-109 |
| packages/canvod-auxiliary/src/canvod/auxiliary/position/spherical\_coords.py |       23 |        0 |    100% |           |
| packages/canvod-auxiliary/src/canvod/auxiliary/preprocessing.py              |       89 |        7 |     92% |115, 119-123, 129 |
| packages/canvod-auxiliary/src/canvod/auxiliary/products/\_\_init\_\_.py      |        3 |        0 |    100% |           |
| packages/canvod-auxiliary/src/canvod/auxiliary/products/models.py            |      103 |       44 |     57% |52-54, 60-63, 108-110, 116-119, 167-176, 192-206, 223-224, 228, 232-247 |
| packages/canvod-auxiliary/src/canvod/auxiliary/products/registry.py          |       27 |       10 |     63% |314-315, 324-334 |
| packages/canvod-auxiliary/test\_download.py                                  |       24 |       18 |     25% | 12-41, 45 |
| packages/canvod-auxiliary/test\_mwe.py                                       |       65 |       58 |     11% |13-116, 120 |
| packages/canvod-auxiliary/tests/conftest.py                                  |       62 |        1 |     98% |        24 |
| packages/canvod-auxiliary/tests/test\_aux\_meta.py                           |       59 |        4 |     93% |18-19, 28-29 |
| packages/canvod-auxiliary/tests/test\_container.py                           |       61 |        0 |    100% |           |
| packages/canvod-auxiliary/tests/test\_internal\_date\_utils.py               |       90 |        0 |    100% |           |
| packages/canvod-auxiliary/tests/test\_internal\_logger.py                    |       33 |        0 |    100% |           |
| packages/canvod-auxiliary/tests/test\_internal\_units.py                     |       31 |        0 |    100% |           |
| packages/canvod-auxiliary/tests/test\_interpolation.py                       |      168 |        0 |    100% |           |
| packages/canvod-auxiliary/tests/test\_pint\_warnings.py                      |       31 |       20 |     35% |24-27, 35-46, 50-66 |
| packages/canvod-auxiliary/tests/test\_position.py                            |      174 |        0 |    100% |           |
| packages/canvod-auxiliary/tests/test\_position\_properties.py                |      152 |        1 |     99% |       477 |
| packages/canvod-auxiliary/tests/test\_preprocessing.py                       |      191 |        0 |    100% |           |
| packages/canvod-auxiliary/tests/test\_products.py                            |      112 |        2 |     98% |   202-203 |
| packages/canvod-grids/src/canvod/grids/\_\_init\_\_.py                       |       26 |        2 |     92% |  179, 184 |
| packages/canvod-grids/src/canvod/grids/\_internal/\_\_init\_\_.py            |        2 |        0 |    100% |           |
| packages/canvod-grids/src/canvod/grids/\_internal/logger.py                  |        5 |        1 |     80% |        26 |
| packages/canvod-grids/src/canvod/grids/aggregation.py                        |      194 |      167 |     14% |78-118, 152-166, 226-335, 358-369, 397-405, 422, 439, 453, 464, 480-484, 492-504, 513-530, 542-601, 613-625, 642-659 |
| packages/canvod-grids/src/canvod/grids/core/\_\_init\_\_.py                  |        4 |        0 |    100% |           |
| packages/canvod-grids/src/canvod/grids/core/grid\_builder.py                 |       36 |        1 |     97% |       111 |
| packages/canvod-grids/src/canvod/grids/core/grid\_data.py                    |      118 |       58 |     51% |83, 87-95, 99, 107, 141-165, 169-208, 240-249 |
| packages/canvod-grids/src/canvod/grids/core/grid\_types.py                   |        9 |        0 |    100% |           |
| packages/canvod-grids/src/canvod/grids/grids\_impl/\_\_init\_\_.py           |        8 |        0 |    100% |           |
| packages/canvod-grids/src/canvod/grids/grids\_impl/equal\_angle\_grid.py     |       33 |        0 |    100% |           |
| packages/canvod-grids/src/canvod/grids/grids\_impl/equal\_area\_grid.py      |       43 |        1 |     98% |       176 |
| packages/canvod-grids/src/canvod/grids/grids\_impl/equirectangular\_grid.py  |       22 |        0 |    100% |           |
| packages/canvod-grids/src/canvod/grids/grids\_impl/fibonacci\_grid.py        |       61 |       51 |     16% |124-133, 144, 171-251, 268-284 |
| packages/canvod-grids/src/canvod/grids/grids\_impl/geodesic\_grid.py         |      100 |        2 |     98% |  142, 226 |
| packages/canvod-grids/src/canvod/grids/grids\_impl/healpix\_grid.py          |       46 |       37 |     20% |117-141, 156, 181-233, 246 |
| packages/canvod-grids/src/canvod/grids/grids\_impl/htm\_grid.py              |       74 |        0 |    100% |           |
| packages/canvod-grids/src/canvod/grids/operations.py                         |      288 |      105 |     64% |180-210, 238-291, 327, 385-392, 399-419, 426-433, 496, 501-546, 682 |
| packages/canvod-grids/src/canvod/grids/workflows/\_\_init\_\_.py             |        2 |        0 |    100% |           |
| packages/canvod-grids/src/canvod/grids/workflows/adapted\_workflow.py        |      187 |      163 |     13% |45-52, 71-73, 105-106, 132-136, 173-227, 277, 334-390, 426-489, 497-508, 517-529, 544-564, 617-695, 716, 735-763 |
| packages/canvod-grids/tests/test\_cell\_assignment.py                        |       86 |        8 |     91% |   123-145 |
| packages/canvod-grids/tests/test\_equal\_area\_grid.py                       |      132 |        0 |    100% |           |
| packages/canvod-grids/tests/test\_grid\_operations.py                        |      109 |        0 |    100% |           |
| packages/canvod-grids/tests/test\_grid\_properties.py                        |      109 |        5 |     95% |     87-97 |
| packages/canvod-grids/tests/test\_grids.py                                   |      146 |        1 |     99% |       263 |
| packages/canvod-grids/tests/test\_grids\_meta.py                             |        3 |        0 |    100% |           |
| packages/canvod-readers/src/canvod/readers/\_\_init\_\_.py                   |        6 |        0 |    100% |           |
| packages/canvod-readers/src/canvod/readers/base.py                           |      126 |       72 |     43% |49-53, 68-99, 119-137, 153-163, 183-186, 309-310, 374, 423-424, 453-470, 488-508, 520 |
| packages/canvod-readers/src/canvod/readers/gnss\_specs/\_\_init\_\_.py       |        0 |        0 |    100% |           |
| packages/canvod-readers/src/canvod/readers/gnss\_specs/bands.py              |      126 |       97 |     23% |171-420, 424-430 |
| packages/canvod-readers/src/canvod/readers/gnss\_specs/constants.py          |       19 |        1 |     95% |        25 |
| packages/canvod-readers/src/canvod/readers/gnss\_specs/constellations.py     |      274 |      113 |     59% |84-86, 102-114, 130-141, 176-256, 261, 348-351, 482-488, 665-671, 770-771, 874-883, 896-906, 961-967, 1018-1024, 1091-1097, 1101-1142 |
| packages/canvod-readers/src/canvod/readers/gnss\_specs/exceptions.py         |       19 |        3 |     84% |54, 100, 162 |
| packages/canvod-readers/src/canvod/readers/gnss\_specs/metadata.py           |       10 |        0 |    100% |           |
| packages/canvod-readers/src/canvod/readers/gnss\_specs/models.py             |      288 |      164 |     43% |93-94, 98-99, 130-136, 159-162, 245, 268, 303, 319, 335, 356-362, 445, 479-482, 522-530, 556-565, 587-610, 655-691, 722-739, 755, 792-825, 875-923, 946-971, 988-997, 1020, 1035-1046, 1089-1105, 1122-1139 |
| packages/canvod-readers/src/canvod/readers/gnss\_specs/signals.py            |       46 |        1 |     98% |       140 |
| packages/canvod-readers/src/canvod/readers/gnss\_specs/utils.py              |       24 |        1 |     96% |        10 |
| packages/canvod-readers/src/canvod/readers/matching/\_\_init\_\_.py          |        3 |        0 |    100% |           |
| packages/canvod-readers/src/canvod/readers/matching/dir\_matcher.py          |       93 |       73 |     22% |64-71, 82-83, 102-110, 129-144, 162, 180-182, 242-248, 264-270, 288-294, 305-334, 345-367 |
| packages/canvod-readers/src/canvod/readers/matching/models.py                |        7 |        0 |    100% |           |
| packages/canvod-readers/src/canvod/readers/rinex/\_\_init\_\_.py             |        2 |        0 |    100% |           |
| packages/canvod-readers/src/canvod/readers/rinex/v3\_04.py                   |      644 |      509 |     21% |148-153, 161-171, 193-338, 348-378, 395-400, 419-428, 445-452, 471-502, 521-529, 548-561, 580-612, 631-640, 645, 649, 657-658, 727-749, 761, 765, 774, 785-792, 804, 816, 828-833, 845-847, 859, 871-875, 893-899, 925-1000, 1008-1053, 1065, 1081-1094, 1121-1124, 1143, 1170-1181, 1188-1203, 1214-1228, 1246-1269, 1298-1325, 1351-1367, 1381-1627, 1665-1698, 1737-1763, 1766-1771, 1774-1819, 1834-1835, 1936-1975 |
| packages/canvod-readers/tests/conftest.py                                    |       19 |        8 |     58% |19, 25-28, 34-36 |
| packages/canvod-readers/tests/test\_gnss\_specs\_base.py                     |      101 |        2 |     98% |   155-156 |
| packages/canvod-readers/tests/test\_readers\_meta.py                         |       38 |        0 |    100% |           |
| packages/canvod-readers/tests/test\_rinex\_integration.py                    |      168 |      108 |     36% |20, 28-37, 41-45, 49-64, 68-96, 100-119, 125-134, 138-152, 158-173, 177-192, 196-211, 215-220, 224-230, 235-247 |
| packages/canvod-readers/tests/test\_rinex\_v3.py                             |      139 |       98 |     29% |19, 27-32, 36-43, 47-55, 59-65, 73-77, 81-84, 88-98, 102-108, 112-118, 122-129, 133-140, 144-151, 155-161, 165-171, 175-181, 189-200, 204-215, 238-242 |
| packages/canvod-readers/tests/test\_signal\_mapping.py                       |      250 |        6 |     98% |433-436, 441-444 |
| packages/canvod-store/src/canvod/store/\_\_init\_\_.py                       |        5 |        0 |    100% |           |
| packages/canvod-store/src/canvod/store/manager.py                            |      217 |      173 |     20% |70-71, 85-92, 101, 106, 115, 120, 150-160, 179-208, 219, 230, 252-265, 290-315, 340-353, 378-395, 423-447, 476-506, 528-563, 574-642, 668-721, 731, 741-743, 762, 767-769 |
| packages/canvod-store/src/canvod/store/reader.py                             |      309 |      275 |     11% |45-63, 86-106, 153-175, 181-184, 188-191, 207, 215-218, 222-225, 239-413, 437-615, 619-622, 627-639, 648-671, 682-689, 699-700, 710-808 |
| packages/canvod-store/src/canvod/store/store.py                              |      914 |      772 |     16% |126-134, 155-158, 176, 243-246, 265, 311, 326-349, 375-400, 420-431, 459-482, 517-578, 583-599, 627-656, 666-699, 723-757, 782-831, 845-883, 915-938, 954, 965-989, 1001-1048, 1080-1149, 1174-1258, 1275-1291, 1308-1323, 1364-1407, 1412-1422, 1442-1494, 1522-1556, 1574-1589, 1595-1597, 1622-1635, 1675-1729, 1766-1918, 1931-1936, 1940, 1944-1945, 1968-2226, 2244-2263, 2267-2271, 2288-2308, 2326-2332, 2361-2387, 2418-2532, 2549-2577, 2611-2643, 2677-2705, 2753-2772, 2777-2798 |
| packages/canvod-store/src/canvod/store/viewer.py                             |      126 |      100 |     21% |33-40, 61, 69, 371-383, 387-407, 426-477, 481-517, 528-610, 647-648, 657-662, 671, 712-723, 740-742 |
| packages/canvod-store/tests/test\_grid\_storage.py                           |      155 |        0 |    100% |           |
| packages/canvod-store/tests/test\_store\_basic.py                            |       10 |        0 |    100% |           |
| packages/canvod-store/tests/test\_store\_crud.py                             |      125 |        0 |    100% |           |
| packages/canvod-store/tests/test\_store\_integrity.py                        |      158 |        0 |    100% |           |
| packages/canvod-utils/src/canvod/utils/\_\_init\_\_.py                       |        2 |        0 |    100% |           |
| packages/canvod-utils/src/canvod/utils/\_meta.py                             |        5 |        0 |    100% |           |
| packages/canvod-utils/src/canvod/utils/config/\_\_init\_\_.py                |        3 |        0 |    100% |           |
| packages/canvod-utils/src/canvod/utils/config/loader.py                      |       83 |       40 |     52% |43-54, 80-82, 106-119, 129-130, 153-154, 158-165, 204-214, 228-233 |
| packages/canvod-utils/src/canvod/utils/config/models.py                      |      135 |       38 |     72% |50-61, 100, 104-108, 275-288, 303, 318, 387, 413-416, 461-465, 475-480, 492, 524, 535 |
| packages/canvod-utils/src/canvod/utils/tools/\_\_init\_\_.py                 |        6 |        0 |    100% |           |
| packages/canvod-utils/src/canvod/utils/tools/date\_utils.py                  |       96 |       14 |     85% |37, 44, 124, 138, 154, 171, 210, 226, 246, 286-287, 328, 383-384 |
| packages/canvod-utils/src/canvod/utils/tools/hashing.py                      |        9 |        6 |     33% |     32-37 |
| packages/canvod-utils/src/canvod/utils/tools/validation.py                   |        7 |        5 |     29% |     29-33 |
| packages/canvod-utils/src/canvod/utils/tools/version.py                      |       16 |       13 |     19% |     28-45 |
| packages/canvod-utils/tests/test\_config.py                                  |       35 |        8 |     77% |24-26, 54-59 |
| packages/canvod-utils/tests/test\_config\_from\_anywhere.py                  |       56 |       38 |     32% |18, 40-74, 80-113 |
| packages/canvod-utils/tests/test\_configuration.py                           |      162 |       59 |     64% |56, 58, 81, 103, 107, 127-128, 159-182, 212-214, 219-253, 257 |
| packages/canvod-viz/src/canvod/viz/\_\_init\_\_.py                           |        6 |        0 |    100% |           |
| packages/canvod-viz/src/canvod/viz/hemisphere\_2d.py                         |      233 |      151 |     35% |106-107, 115, 184, 190-199, 223, 246-288, 292-366, 371, 376, 441, 487-488, 539-665 |
| packages/canvod-viz/src/canvod/viz/hemisphere\_3d.py                         |      174 |      112 |     36% |126-130, 184, 215-216, 242-277, 301-323, 429-521, 552-595, 624-689, 747-758 |
| packages/canvod-viz/src/canvod/viz/styles.py                                 |       49 |        0 |    100% |           |
| packages/canvod-viz/src/canvod/viz/visualizer.py                             |       52 |        3 |     94% |244, 349-350 |
| packages/canvod-viz/tests/test\_integration.py                               |      235 |        1 |     99% |       508 |
| packages/canvod-viz/tests/test\_viz.py                                       |       88 |        0 |    100% |           |
| packages/canvod-viz/tests/test\_viz\_meta.py                                 |       32 |        0 |    100% |           |
| packages/canvod-vod/src/canvod/vod/\_\_init\_\_.py                           |        3 |        0 |    100% |           |
| packages/canvod-vod/src/canvod/vod/\_internal/\_\_init\_\_.py                |        2 |        0 |    100% |           |
| packages/canvod-vod/src/canvod/vod/\_internal/logger.py                      |        5 |        1 |     80% |        26 |
| packages/canvod-vod/src/canvod/vod/calculator.py                             |       64 |       15 |     77% |51, 65, 98-112, 214-220 |
| packages/canvod-vod/tests/test\_vod\_basic.py                                |        8 |        0 |    100% |           |
| packages/canvod-vod/tests/test\_vod\_calculator.py                           |      113 |        1 |     99% |       359 |
| packages/canvod-vod/tests/test\_vod\_meta.py                                 |        3 |        0 |    100% |           |
| packages/canvod-vod/tests/test\_vod\_properties.py                           |      138 |        9 |     93% |27, 36, 45, 183, 235, 299, 466, 469, 481 |
| test\_factories.py                                                           |       64 |       22 |     66% |14-16, 26-28, 37-39, 55, 60, 65-72, 85-90 |
| test\_new\_api.py                                                            |       68 |       23 |     66% |17-22, 30, 36-41, 48-52, 67-71, 77-78, 94-95 |
| **TOTAL**                                                                    | **13211** | **6180** | **53%** |           |


## Setup coverage badge

Below are examples of the badges you can use in your main branch `README` file.

### Direct image

[![Coverage badge](https://raw.githubusercontent.com/nfb2021/canvodpy/python-coverage-comment-action-data/badge.svg)](https://htmlpreview.github.io/?https://github.com/nfb2021/canvodpy/blob/python-coverage-comment-action-data/htmlcov/index.html)

This is the one to use if your repository is private or if you don't want to customize anything.

### [Shields.io](https://shields.io) Json Endpoint

[![Coverage badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/nfb2021/canvodpy/python-coverage-comment-action-data/endpoint.json)](https://htmlpreview.github.io/?https://github.com/nfb2021/canvodpy/blob/python-coverage-comment-action-data/htmlcov/index.html)

Using this one will allow you to [customize](https://shields.io/endpoint) the look of your badge.
It won't work with private repositories. It won't be refreshed more than once per five minutes.

### [Shields.io](https://shields.io) Dynamic Badge

[![Coverage badge](https://img.shields.io/badge/dynamic/json?color=brightgreen&label=coverage&query=%24.message&url=https%3A%2F%2Fraw.githubusercontent.com%2Fnfb2021%2Fcanvodpy%2Fpython-coverage-comment-action-data%2Fendpoint.json)](https://htmlpreview.github.io/?https://github.com/nfb2021/canvodpy/blob/python-coverage-comment-action-data/htmlcov/index.html)

This one will always be the same color. It won't work for private repos. I'm not even sure why we included it.

## What is that?

This branch is part of the
[python-coverage-comment-action](https://github.com/marketplace/actions/python-coverage-comment)
GitHub Action. All the files in this branch are automatically generated and may be
overwritten at any moment.