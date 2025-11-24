class GestureMapper:
    def map(self, landmarks):
        """
        Input: landmarks (list dari 21 titik tangan)
        Output: 'A', 'B', 'C', 'D', atau None
        """

        if landmarks is None:
            return None

        # Ambil titik penting
        thumb_tip  = landmarks[4]   # ujung jempol
        index_tip  = landmarks[8]   # ujung telunjuk
        middle_tip = landmarks[12]  # ujung jari tengah
        ring_tip   = landmarks[16]
        pinky_tip  = landmarks[20]

        # ------------------------------------------
        # RULE DASAR (bisa kamu tweak nanti)
        # ------------------------------------------

         # D = ✊ (semua jari turun: perbedaan kecil antar titik)
        if (
            abs(index_tip[1] - middle_tip[1]) < 25 and
            abs(middle_tip[1] - ring_tip[1]) < 25 and
            abs(ring_tip[1] - pinky_tip[1]) < 25
        ):
            return "D"
        
        # A = 👍 (jempol paling atas)
        if thumb_tip[1] < index_tip[1] and thumb_tip[1] < middle_tip[1]:
            return "A"

        # B = ✌️ (dua jari menghadap atas: telunjuk & tengah)
        if index_tip[1] < thumb_tip[1] and middle_tip[1] < thumb_tip[1]:
            return "B"

        # C = ☝️ (hanya telunjuk yang naik)
        if index_tip[1] < middle_tip[1] and index_tip[1] < ring_tip[1]:
            return "C"

       

        return None
