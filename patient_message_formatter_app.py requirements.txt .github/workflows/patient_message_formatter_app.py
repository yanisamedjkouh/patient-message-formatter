import re
import tkinter as tk
from tkinter import messagebox


def normalize_text(text: str) -> str:
    return text.replace("\r", "\n").strip()


def clean_line(line: str) -> str:
    return re.sub(r"\s+", " ", line.strip())


def extract_lines(text: str):
    return [clean_line(line) for line in normalize_text(text).split("\n") if clean_line(line)]


def extract_name(lines):
    for line in lines:
        lower = line.lower()
        if not any(keyword in lower for keyword in [
            "year", "old", "cm", "kg", "disease", "infection", "surgery", "medication",
            "allergy", "alcohol", "smoke", "height", "weight", "age"
        ]):
            if re.search(r"[a-zA-Z]", line):
                return line
    return ""


def extract_age(text: str):
    match = re.search(r"(\d{1,3})\s*(?:years?\s*old|yo|y/o|age)?", text, re.IGNORECASE)
    if match:
        age = int(match.group(1))
        if 1 <= age <= 120:
            return str(age)
    return ""


def extract_height_cm(text: str):
    lower = text.lower()

    # Matches formats like: 1 m 76 cm, 1m76, 1.76 m, 1,76 m
    match = re.search(r"(\d)\s*(?:m|meter|meters)\s*[,\.]?\s*(\d{1,2})\s*(?:cm|sm)?", lower)
    if match:
        meters = int(match.group(1))
        centimeters = int(match.group(2))
        return meters * 100 + centimeters

    match = re.search(r"(\d)[\.,](\d{2})\s*(?:m|meter|meters)?", lower)
    if match:
        meters = int(match.group(1))
        centimeters = int(match.group(2))
        return meters * 100 + centimeters

    # Matches direct cm format: 176 cm / 176 sm
    match = re.search(r"\b(1[3-9]\d|2[0-2]\d)\s*(?:cm|sm)\b", lower)
    if match:
        return int(match.group(1))

    return None


def extract_weight_kg(text: str):
    lower = text.lower()
    match = re.search(r"\b(\d{2,3})\s*(?:kg|kgs|kilograms?)\b", lower)
    if match:
        weight = int(match.group(1))
        if 25 <= weight <= 300:
            return weight
    return None


def calculate_bmi(height_cm, weight_kg):
    if not height_cm or not weight_kg:
        return ""
    height_m = height_cm / 100
    bmi = weight_kg / (height_m ** 2)
    return str(round(bmi))


def answer_none(line: str) -> bool:
    lower = line.lower()
    none_patterns = [
        "no", "none", "nothing", "i don't", "i dont", "don’t", "do not", "no any",
        "not have", "don't have", "dont have", "not taking", "i don’t take", "i dont take"
    ]
    return any(pattern in lower for pattern in none_patterns)


def answer_yes(line: str) -> bool:
    lower = line.lower()
    return any(word in lower for word in ["yes", "i had", "had surgery", "before", "previous surgery", "operation"])


def find_answer(lines, topic_keywords, default=""):
    for line in lines:
        lower = line.lower()
        if any(keyword in lower for keyword in topic_keywords):
            return line
    return default


def format_none_yes_answer(raw_answer: str, yes_label="Yes *"):
    if not raw_answer:
        return ""
    if answer_none(raw_answer):
        return "None"
    if answer_yes(raw_answer):
        return yes_label
    return raw_answer


def format_smoking_alcohol(raw_answer: str):
    if not raw_answer:
        return ""
    lower = raw_answer.lower()

    has_smoke = any(word in lower for word in ["smoke", "smoking", "cigarette"])
    has_alcohol = any(word in lower for word in ["alcohol", "drink", "drinks", "wine", "beer"])
    occasional = any(word in lower for word in ["sometimes", "occasionally", "social", "rarely"])

    if answer_none(raw_answer) and not has_smoke and not has_alcohol:
        return "None"
    if occasional and has_smoke and has_alcohol:
        return "Occasionally smoke and drinks"
    if occasional and has_smoke:
        return "Occasionally smokes"
    if occasional and has_alcohol:
        return "Occasionally drinks alcohol"
    return raw_answer


def parse_patient_text(text: str):
    lines = extract_lines(text)
    full_text = "\n".join(lines)

    name = extract_name(lines)
    age = extract_age(full_text)
    height_cm = extract_height_cm(full_text)
    weight_kg = extract_weight_kg(full_text)
    bmi = calculate_bmi(height_cm, weight_kg)

    chronic_raw = find_answer(lines, ["disease", "diseases", "chronic", "diabetes", "hypertension"])
    infection_raw = find_answer(lines, ["infection", "infections", "infectious", "hiv", "hepatitis"])
    surgery_raw = find_answer(lines, ["surgery", "surgeries", "operation", "operated"])
    medication_raw = find_answer(lines, ["medication", "medications", "medicine", "take", "regularly"])
    allergy_raw = find_answer(lines, ["allergy", "allergies", "allergic"])
    smoke_alcohol_raw = find_answer(lines, ["smoke", "smoking", "alcohol", "drink", "drinks"])

    chronic = format_none_yes_answer(chronic_raw, yes_label=chronic_raw)
    infection = format_none_yes_answer(infection_raw, yes_label=infection_raw)
    surgery = format_none_yes_answer(surgery_raw, yes_label="Yes *")
    medication = format_none_yes_answer(medication_raw, yes_label=medication_raw)
    allergy = format_none_yes_answer(allergy_raw, yes_label=allergy_raw)
    smoke_alcohol = format_smoking_alcohol(smoke_alcohol_raw)

    formatted = f"""*Personal Information*
1. Full Name: {name}
2. Age: {age} Yo
3. Height: {height_cm if height_cm else ''} cm
4. Weight: {weight_kg if weight_kg else ''} kg 
5. BMI = {bmi}

*Medical History*
1. Do you have any chronic diseases? {chronic}
2. Do you have any infectious diseases? {infection}
3. Have you had any previous surgeries? {surgery}

*Medications and Allergies*
1. Do you take any medications regularly? {medication}
2. Do you have any allergies? {allergy}
3. Do you smoke or consume alcohol? {smoke_alcohol}"""

    return formatted


class PatientFormatterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Patient Message Formatter")
        self.root.geometry("1050x650")
        self.root.minsize(900, 550)

        title = tk.Label(
            root,
            text="Patient Message Formatter",
            font=("Arial", 18, "bold")
        )
        title.pack(pady=10)

        main_frame = tk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)

        left_frame = tk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 6))

        right_frame = tk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(6, 0))

        tk.Label(left_frame, text="Paste patient answer here:", font=("Arial", 11, "bold")).pack(anchor="w")
        self.input_text = tk.Text(left_frame, wrap=tk.WORD, font=("Arial", 11))
        self.input_text.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

        tk.Label(right_frame, text="Formatted message for doctor:", font=("Arial", 11, "bold")).pack(anchor="w")
        self.output_text = tk.Text(right_frame, wrap=tk.WORD, font=("Arial", 11))
        self.output_text.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

        button_frame = tk.Frame(root)
        button_frame.pack(fill=tk.X, padx=12, pady=10)

        format_button = tk.Button(
            button_frame,
            text="Format Message",
            command=self.format_message,
            font=("Arial", 11, "bold"),
            height=2
        )
        format_button.pack(side=tk.LEFT, padx=(0, 8))

        copy_button = tk.Button(
            button_frame,
            text="Copy Result",
            command=self.copy_result,
            font=("Arial", 11),
            height=2
        )
        copy_button.pack(side=tk.LEFT, padx=8)

        clear_button = tk.Button(
            button_frame,
            text="Clear",
            command=self.clear_all,
            font=("Arial", 11),
            height=2
        )
        clear_button.pack(side=tk.LEFT, padx=8)

        sample_button = tk.Button(
            button_frame,
            text="Load Sample",
            command=self.load_sample,
            font=("Arial", 11),
            height=2
        )
        sample_button.pack(side=tk.LEFT, padx=8)

    def format_message(self):
        raw_text = self.input_text.get("1.0", tk.END).strip()
        if not raw_text:
            messagebox.showwarning("Missing Text", "Please paste the patient's answer first.")
            return

        formatted = parse_patient_text(raw_text)
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, formatted)

    def copy_result(self):
        result = self.output_text.get("1.0", tk.END).strip()
        if not result:
            messagebox.showwarning("Nothing to Copy", "Please format a message first.")
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(result)
        self.root.update()
        messagebox.showinfo("Copied", "Formatted message copied to clipboard.")

    def clear_all(self):
        self.input_text.delete("1.0", tk.END)
        self.output_text.delete("1.0", tk.END)

    def load_sample(self):
        sample = """Natalja Repnikova 
47 years old 
1 m 76 sm
60 kg

I don’t have any diseases 
No any infections 
I had surgery before 

I don’t take any medication 
No any allergy 
Sometimes alcohol and some smoke"""
        self.clear_all()
        self.input_text.insert(tk.END, sample)


if __name__ == "__main__":
    root = tk.Tk()
    app = PatientFormatterApp(root)
    root.mainloop()
