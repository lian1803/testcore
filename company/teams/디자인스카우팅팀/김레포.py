"""
김레포 — Design System Repository Scanner
Scans available effects in design_system and suggests underused ones
"""

import json
import os
from datetime import datetime
from pathlib import Path


class DesignSystemScanner:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.design_system_path = Path(__file__).parent.parent.parent.parent / "design_system"
        self.backgrounds_dir = self.design_system_path / "components/react-bits/src/content/Backgrounds"
        self.text_animations_dir = self.design_system_path / "components/react-bits/src/content/TextAnimations"
        self.results = {
            "backgrounds": [],
            "text_animations": [],
            "recommendations": [],
            "timestamp": datetime.now().isoformat()
        }

    def load_used_effects(self):
        """Load previously used effects from JSON"""
        used_file = self.base_dir / "used_effects.json"
        if used_file.exists():
            with open(used_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"backgrounds": set(), "text_animations": set()}

    def scan_directory(self, directory: Path, effect_type: str):
        """Scan a directory for effect files"""
        if not directory.exists():
            print(f"[WARNING] Directory not found: {directory}")
            return []

        effects = []
        for file in directory.rglob("*.tsx"):
            try:
                with open(file, "r", encoding="utf-8") as f:
                    content = f.read()
                    # Extract first comment as description
                    description = ""
                    lines = content.split("\n")
                    for line in lines[:10]:
                        if "//" in line or "/*" in line or "*" in line:
                            description = line.replace("//", "").replace("/*", "").replace("*/", "").strip()
                            if description:
                                break

                    effects.append({
                        "name": file.stem,
                        "file": file.name,
                        "description": description or "(No description)"
                    })
            except Exception as e:
                print(f"  [WARNING] Error reading {file.name}: {e}")

        return effects

    def get_recommendations(self, all_effects: dict, used_effects: dict):
        """Suggest top 3 underused effects"""
        recommendations = []

        for effect_type in ["backgrounds", "text_animations"]:
            available = all_effects.get(effect_type, [])
            used = used_effects.get(effect_type, set())

            # Filter to underused effects
            underused = [e for e in available if e["name"] not in used]

            # Pick top 3
            for effect in underused[:3]:
                recommendations.append({
                    "type": effect_type,
                    "name": effect["name"],
                    "description": effect["description"],
                    "reason": "Not used recently in projects"
                })

        return recommendations

    def run(self):
        """Execute scanning"""
        print("[START] Design system repo scanner starting...")

        # Scan backgrounds
        print("  [SCAN] Scanning backgrounds...")
        backgrounds = self.scan_directory(self.backgrounds_dir, "backgrounds")
        self.results["backgrounds"] = backgrounds
        print(f"    [SUCCESS] Found {len(backgrounds)} background effects")

        # Scan text animations
        print("  [SCAN] Scanning text animations...")
        text_anims = self.scan_directory(self.text_animations_dir, "text_animations")
        self.results["text_animations"] = text_anims
        print(f"    [SUCCESS] Found {len(text_anims)} text animation effects")

        # Load used effects and get recommendations
        used = self.load_used_effects()
        all_effects = {
            "backgrounds": backgrounds,
            "text_animations": text_anims
        }
        recommendations = self.get_recommendations(all_effects, used)
        self.results["recommendations"] = recommendations

        print(f"  [RECOMMEND] Generated {len(recommendations)} recommendations")

        # Save results
        results_file = self.base_dir / "repo_results.json"
        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)

        print(f"\n[SUCCESS] Design system repo scanner completed: {len(backgrounds) + len(text_anims)} effects scanned")
        return self.results


if __name__ == "__main__":
    scanner = DesignSystemScanner()
    scanner.run()
