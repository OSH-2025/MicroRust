# 操作系统概述
##### 常见的操作系统
> 1. 桌面操作系统：Windows，macOS，Linux.
> 2. 移动操作系统：Android，iOS，HarmonyOS.
> 3. 服务器操作系统：Linux，Windows Server.
> 4. 嵌入式与实时操作系统：FreeRTOS，RTEMS，VxWorks.
##### Rust改写难度
> 根据ChatGPT的反馈，嵌入式与实时操作系统的改写难度最小，桌面操作系统的改写难度最大.
# 历年作品回顾
##### 桌面操作系统改写
> 1. Rust改写Linux内核的一部分.
##### 嵌入式与实时操作系统改写
> 1. Rust改写HuaWei LiteOS的内存管理单元(MMU).
> 2. Rust改写Harmony LiteOS-M.
> 3. Rust改写FreeRTOS.
> 4. Rust改写seL4微内核.
> 5. Rust改写Unikraft.
##### 操作系统相关开发
> 1. OSH-2020/x-chital.
> 2. OSH-2020/x-gkd.
> 3. OSH-2022/x-realism.
> 4. OSH-2023/Actus_Neopiritus.
# 推荐列表
### 总结
> 我们可以发现前人的项目主要集中在嵌入式与实时操作系统改写，同时也涉及Linux改进和操作系统相关功能的独立开发。基于此，我提出以下四个项目选题，前两个围绕实时操作系统改写，第三个围绕Linux内核的调试和诊断工具的改写和易使用性改进，最后一个与神经网络计算专用的操作系统有关.
##### Rust改写国产开源实时操作系统RT-Thread.
> RT-Thread是一个成熟的国产开源实时操作系统，可以在RT-Thread官方GitHub仓库找到源代码.
##### Rust改写FreeRTOS的内存管理部分，并尝试解决其缺少动态内存分配机制的问题.
> FreeRTOS默认没有提供动态内存分配的良好机制，尤其是在内存紧张的嵌入式系统中，使用 malloc()和 free()可能导致内存碎片问题，并且其内存分配策略并不适合实时应用；FreeRTOS的堆管理仅提供有限的内存管理机制，如heap_4.c和heap_5.c，但缺乏更先进的内存管理方案，如内存池、动态内存分配优化等。我们可以通过Rust改写FreeRTOS的内存管理部分，并添加上述功能.
##### Rust改写Linux内核的调试和诊断工具，并改善其易使用性.
> Linux内核拥有非常多样的调试和诊断工具，但对于初学者来说，使用这些工具较为困难.因此，可以考虑使用Rust开发易于操作的Linux内核调试工具.Rust在内存安全、并发处理和性能方面具有优势，但它在与现有内核调试工具（主要使用C语言实现）整合时仍面临技术挑战，目前，Rust更适合用于开发用户空间调试工具或一些较简单的调试和性能分析功能.适合用 Rust改写的调试工具有ftrace、perf、kdb/kgdb、strace、LTTng、systemtap、dmesg，这些工具可以受益于Rust的内存安全性、并发性和高效性能，尤其是在资源有限和要求高稳定性的嵌入式或内核级调试任务中.
##### 基于Rust开发神经网络计算专用的操作系统.
> 神经网络专用的操作系统（Neural Network Operating Systems, NNOS）是针对人工智能（AI）和深度学习（Deep Learning）的特定需求而设计的操作系统。这些操作系统旨在优化和提升神经网络、机器学习和计算密集型任务的性能，通常与专用硬件（如GPUTPUFPGA、ASIC等）紧密集成，以最大化神经网络的计算能力。目前常用的NNOS有TensorFlow Lite OS，为嵌入式设备提供神经网络优化的推理引擎。TensorFlow Lite OS是TensorFlow Lite项目的一部分，我们可以从TensorFlow的GitHub仓库中获取相关代码，用Rust改写并将其集成到其他嵌入式操作系统（如FreeRTOS、RT-Thread等）上.