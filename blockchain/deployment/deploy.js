const { ethers } = require("hardhat");

async function main() {
  const SatyaVerify = await ethers.getContractFactory("SatyaVerifyProvenance");
  const satyaVerify = await SatyaVerify.deploy();
  await satyaVerify.waitForDeployment();
  const address = await satyaVerify.getAddress();
  console.log("SatyaVerifyProvenance deployed to:", address);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
