from base import *
from devices import *

class SonySpresense(Board):

    @staticmethod
    def match(dev):
        return dev["vid"]=="10C4" and dev["pid"] =="EA60"

    def probing_pre_v_hook(self):
        time.sleep(0.2)

    def reset(self):
        conn = ConnectionInfo()
        conn.set_serial(self.port,**self.connection)
        ch = Channel(conn)
        try:
            ch.open(timeout=2)
            # Target Reset by DTR
            ch.ch.setDTR(False)
            ch.ch.setDTR(True)
            ch.ch.setDTR(False)
            ch.close()
        except:
            fatal("Can't open serial:",self.port)

    def burn(self,bin,outfn=None):
        nuttx = fs.get_tempfile(bin)
        td = fs.get_tempdir()
        nuttx_spk = fs.path(td,"nuttx.spk")
        res, out, err = proc.runcmd("spresense_mkspk", "-c", "2", nuttx, "nuttx", nuttx_spk, outfn=outfn)
        res, out, err = proc.runcmd("spresense_flashwriter", "-s", "-c", self.port, "-d", "-b", "115200", "-n", nuttx_spk, outfn=outfn)
        fs.del_tempfile(nuttx_spk)
        fs.del_tempfile(nuttx)
        if res:
            return False,out
        return True,out

    def burn_bootloader(self, action_param=None, outfn=None):
        if action_param:
            if "accept" in action_param and not "decline" in action_param:
                cur_path = os.getcwd()
                firmware_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "firmware")

                os.chdir(firmware_path)
                res, out, err = proc.runcmd("spresense_flashwriter", "-s", "-c", self.port, "-d", "-b", "115200", "-n", "AESM.espk", "dnnrt-mp.espk", "gnssfw.espk", "loader.espk", outfn=outfn)

                os.chdir(cur_path)
            return True, ""

        eula_msg = """In order to flash Spresense Bootloader you have to read carefully and accept the following EULA: <a href="https://developer.sony.com/eula/eula-spresense-board-recovery-tool" target="_blank">https://developer.sony.com/eula/eula-spresense-board-recovery-tool</a>"""
        return True, {"text": eula_msg, "params": ["accept", "decline"], "title": "Spresense EULA"}


