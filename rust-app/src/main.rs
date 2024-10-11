use tch::{Device, Tensor};
use std::env;

fn main() -> Result<(), tch::TchError> {
    let exe_path = env::current_exe()?;
    let model_path = exe_path.parent().unwrap().join("RegressionModel-BEST-2024-05-23-02-06-28.pt");

    println!("Running model:\n{}", model_path.display());

    let model = tch::CModule::load(&model_path)?;
    let var_store = tch::nn::VarStore::new(Device::cuda_if_available());
    let image = Tensor::randn(&[1, 1, 420, 220], (tch::Kind::Float, var_store.device()));
    let output = model.forward_ts(&[image])?;

    println!("\nOutput:\n{}", output.get(0));

    std::io::stdin().read_line(&mut String::new())?;
    Ok(())
}