from utils import sdk, libecap, logger, inspect_class

inspect_class(libecap.EegSignalGain)
inspect_class(libecap.EegSignalSource)
inspect_class(libecap.EegSampleRate)
inspect_class(libecap.ImuSampleRate)
# inspect_class(bc_ecap_sdk.BandPassFilter)

fs = 250  # 采样频率
low_cut = 2  # 低通滤波截止频率
high_cut = 45  # 高通滤波截止频率
bs = sdk.BandPassFilter(fs, low_cut, high_cut)
print(bs)
test_data = [1, 2, 3, 4, 5]

for i in range(10):
    filter_data = bs.filter(test_data)
    print(filter_data)


# TODO:
# 1. receive data timestamp issue
# 2. crc check failed, may be the data is lost
# 3. loop check impendance issue

b = b"BRNC\x02\x0c$\x00\x03\x01\x00Z\x10\x1a\x04\x08\x03\x10\x02%\x00\x00\x009-\x00\x00z=j\t\x12\x02\x08\x02\x1d\x00\x00\xc8:\xaa\x01\x04\x1a\x02\x08\x03u\xb6"
print(",".join(f"{x:02x}" for x in b))

b = b'BRNC\x02\x0c2\x00\x03\x01\x00\x120\x08\x07"\x050.0.1*\x050.2.42\x132024-11-26 18:26:56:\x07bd919e4@Fq\xe1'
print(",".join(f"{x:02x}" for x in b))
