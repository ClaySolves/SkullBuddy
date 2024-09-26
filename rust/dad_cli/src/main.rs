use eframe::{egui, App};
use std::process::Command;
use std::str;

fn main() -> Result<(), eframe::Error> {
    let options = eframe::NativeOptions::default();
    eframe::run_native(
        "SquireBot",  // Title of your GUI 💻
        options,
        Box::new(|_cc| Box::new(MyApp::default())),
    )
}

#[derive(Default)]
struct MyApp {
    check1: bool,
    check2: bool,
    check3: bool,
    sell_stash: String,
    store_stash: String,
}

impl App for MyApp {
    fn update(&mut self, ctx: &egui::Context, _frame: &mut eframe::Frame) {
        egui::CentralPanel::default().show(ctx, |ui| {
            ui.heading("Squire-Bot");

            ui.checkbox(&mut self.check1, "Checkbox 1: Placeholder Text 1");
            ui.checkbox(&mut self.check2, "Checkbox 2: Placeholder Text 2");
            ui.checkbox(&mut self.check3, "Checkbox 3: Placeholder Text 3");

            ui.label("Sell from stash: ");
            ui.text_edit_singleline(&mut self.sell_stash);

            ui.label("Store in stash: ");
            ui.text_edit_singleline(&mut self.store_stash);

            if ui.button("Sell Items").clicked() {
                println!("Running Script...");

                let script_path = r"C:\\main/darkAndDarker/autoTradingPost/python/main.py";
                let script_output = Command::new("runas")
                    .arg("/user:Administrator")
                    .arg(format!("python {}", script_path))
                    .output()
                    .expect("Failed to execute script");

                let stdout = str::from_utf8(&script_output.stdout).expect("Failed to parse output");
                let stderr = str::from_utf8(&script_output.stderr).expect("Failed to parse error");

                if !stdout.is_empty() {
                    println!("Python Output: {}", stdout);
                }
            
                if !stderr.is_empty() {
                    eprintln!("Python Error: {}", stderr);
                }

                if self.check1 {
                    println!("Checkbox 1 is checked");
                }
                if self.check2 {
                    println!("Checkbox 2 is checked");
                }
                if self.check3 {
                    println!("Checkbox 3 is checked");
                }
            }
        });
    }
}
