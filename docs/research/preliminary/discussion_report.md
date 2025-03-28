本次讨论讨论中,我们小组的进行了2份"Rust为FreeRTOS设计基于机器学习的任务预测调度器"的调研,3份"Rust改写FreeRTOS的内存管理模块"的调研.我们经过讨论后,发现这两个项目选题各有优缺点,以下是这两个项目的优缺点分析,希望邢老师可以在选题上为我们提供相关的建议.
# Rust为FreeRTOS设计基于机器学习的任务预测调度器
## 优点
> 1. 组员对于硬件熟悉度较低,对于软件较为熟悉.
> 2. 最为困难的部分在于数据的获取与处理,相对来说rust改写部分是较为简单的.
> 3. 人工智能的库在python中大多都有调用,在了解了机理和获取了数据后操作相对简答.
> 4. 最终可以不用上开发板,而仅仅只对比修改前后在虚拟机上跑的性能
## 缺点
> 1. 组员对于机器学习学习大都较少,可能出现模型没选好,参数没选好.
> 2. 如果最终函数参数的过于复杂,占用的空间时间过多,会导致跑出来性能比原来还差.
> 3. (**最为关键**)数据缺少,我们能得到的数据不知道是否与运行时间等性能具有强烈的关联,可能跑出来的函数实用性差.
> 4. 不同程序任务不一样,虽然是嵌入式系统运行程序较为单一,可能会出现普适性较差的情况.
# Rust改写FreeRTOS的内存管理模块
## 优点
> 1. FreeRTOS自带内存管理功能,小组在其原有C语言文件的基础上进行Rust改写和改进较为简单.
> 2. 小组对内存管理模块的Rust改写可以确保提高FreeRTOS的内存安全性,保证改写后的操作系统性能不劣于改写前的.
> 3. FreeRTOS为资源受限的嵌入式系统设计,因此可以在不支持mmu的硬件上运行.
## 缺点
> 1. 小组对内存管理的调试工具了解较少,可能在改写完成后缺少调优的手段.
> 2. 小组对内存管理了解较少,可能无法实现有效的内存管理优化.
> 3. FreeRTOS改写后的版本首先会在虚拟机上测试,但是虚拟机可能无法真实反映操作系统对于硬件内存的管理,在虚拟机上的测试可能无法反映小组的改写成果.
> 4. 内存管理的优化可能需要在硬件设备上实验以获得最好的实验结果,小组无法保证能在单片机上顺利搭建FreeRTOS操作系统.