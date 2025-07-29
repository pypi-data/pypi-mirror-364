use crc16::{State, MODBUS};
// crate::cfg_import_logging!();

pub fn calculate_crc16_modbus(data: &[u8]) -> u16 {
  State::<MODBUS>::calculate(data)
}

// use crc32fast::Hasher;
// pub fn calculate_crc32(data: &[u8]) -> u32 {
//   let mut hasher = Hasher::new();
//   hasher.update(data);
//   hasher.finalize()
// }

/*
 * The CRC polynomial and other parameters were found using
 * CRC reveng. They are:
 * 	width=32
 *	poly=0x04c11db7
 *	init=0xffffffff
 *	refin=false
 *	refout=false
 *	xorout=0x00000000
 *	check=0x0376e6e7
 *  residue=0x00000000
 */
// pub const CRC_32_MPEG_2: Algorithm<u32> = Algorithm {
//   width: 32,
//   poly: 0x04c11db7,
//   init: 0xffffffff,
//   refin: false,
//   refout: false,
//   xorout: 0x00000000,
//   check: 0x0376e6e7,
//   residue: 0x00000000,
// };
// use crc::{crc32, Hasher32};
// use crc::{Algorithm, Crc, CRC_32_MPEG_2};
// pub fn calculate_crc32(data: &[u8]) -> u32 {
//   const CRC32: Crc<u32> = Crc::<u32>::new(&CRC_32_MPEG_2);
//   let mut digest = CRC32.digest();
//   digest.update(data);
//   digest.finalize()
// }

pub fn calculate_crc32(data: &[u8]) -> u32 {
  const POLYNOMIAL: u32 = 0x04C11DB7; // CRC-32标准多项式
  let crc32 = CRC32::new(POLYNOMIAL);
  crc32.compute(data)
}

pub fn stark_calculate_crc32(data: &[u8]) -> u32 {
  let crc32 = CRC32::new(0x04C11DB7);
  crc32.stark_compute(data)
}

pub struct CRC32 {
  table: [u32; 256],
}

impl CRC32 {
  /// Creates a new CRC32 instance with the given polynomial
  pub fn new(poly: u32) -> Self {
    let table = generate_crc32_table(poly);
    CRC32 { table }
  }

  /// Computes the CRC32 checksum for the given data
  pub fn compute(&self, data: &[u8]) -> u32 {
    let seed = 0xFFFFFFFF;
    let final_xor = 0x00000000;
    let mut n_reg = seed;

    let num_iterations = data.len() / 4;
    for i in 0..num_iterations {
      let mut buffer = 0u32;
      for j in 0..4 {
        buffer |= (data[i * 4 + j] as u32) << (j * 8);
      }
      n_reg ^= buffer;
      for _ in 0..4 {
        let index = ((n_reg >> 24) & 0xFF) as u8;
        let n_temp = self.table[index as usize];
        n_reg <<= 8;
        n_reg ^= n_temp;
      }
    }
    n_reg ^ final_xor
  }

  pub fn stark_compute(&self, data: &[u8]) -> u32 {
    let mut n_reg = 0xFFFFFFFF; // 初始值

    // 按4字节处理
    let chunks = data.chunks(4);
    for chunk in chunks {
      // 小端序构造32位数据
      let mut word = 0u32;
      for (i, &byte) in chunk.iter().enumerate() {
        word |= (byte as u32) << (i * 8);
      }

      n_reg ^= word;
      // 32位CRC计算
      for _ in 0..32 {
        n_reg = if (n_reg & 0x80000000) != 0 {
          (n_reg << 1) ^ 0x04C11DB7
        } else {
          n_reg << 1
        };
      }
    }

    n_reg
  }
}

#[allow(dead_code)]
pub(crate) const fn crc32_table(width: u8, poly: u32, reflect: bool) -> [u32; 256] {
  let poly = if reflect {
    let poly = poly.reverse_bits();
    poly >> (32u8 - width)
  } else {
    poly << (32u8 - width)
  };

  let mut table = [0u32; 256];
  let mut i = 0;
  while i < 256 {
    table[i] = crc32(poly, reflect, i as u32);
    i += 1;
  }

  table
}

#[allow(dead_code)]
pub(crate) const fn crc32(poly: u32, reflect: bool, mut value: u32) -> u32 {
  if reflect {
    let mut i = 0;
    while i < 8 {
      value = (value >> 1) ^ ((value & 1) * poly);
      i += 1;
    }
  } else {
    value <<= 24;

    let mut i = 0;
    while i < 8 {
      value = (value << 1) ^ (((value >> 31) & 1) * poly);
      i += 1;
    }
  }
  value
}

#[allow(dead_code)]
fn generate_crc32_table_2(poly: u32) -> [u32; 256] {
  let mut table = [0u32; 256];
  #[allow(clippy::needless_range_loop)]
  for i in 0..256 {
    let mut crc = (i as u32) << 24;
    for _ in 0..8 {
      if crc & 0x80000000 != 0 {
        crc = (crc << 1) ^ poly;
      } else {
        crc <<= 1;
      }
    }
    table[i] = crc;
  }
  table
}

fn generate_crc32_table(poly: u32) -> [u32; 256] {
  // let table = crc32_table(32, poly, false);
  let table = generate_crc32_table_2(poly);
  // for i in 0..256 {
  //   info!("{:08X}, ", table[i]);
  // }
  #[allow(clippy::let_and_return)]
  table
}
