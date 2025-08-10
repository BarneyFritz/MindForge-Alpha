from typing import List

class ContradictionDetector:
    def find_contradictions(self, responses: List[str]) -> List[str]:
        contradictions: List[str] = []
        lowers = [r.lower() for r in responses]
        if any("should" in r for r in lowers) and any("should not" in r for r in lowers):
            contradictions.append("Detected opposing directives (should vs should not)")
        return contradictions