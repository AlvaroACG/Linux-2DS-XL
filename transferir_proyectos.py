from pathlib import Path
import ftplib,io,hashlib,time,json,uuid
r=Path(r'C:\Users\alvar\Desktop');files=[]
for p in (r/'Linux-2DS-XL/PARA COPIAR A LA SD').rglob('*'):
 if p.is_file():files.append((p,'/'+p.relative_to(r/'Linux-2DS-XL/PARA COPIAR A LA SD').as_posix()))
for p in (r/'WoW-3DS/PARA COPIAR A LA SD').rglob('*'):
 if p.is_file():files.append((p,'/'+p.relative_to(r/'WoW-3DS/PARA COPIAR A LA SD').as_posix()))
files.extend([(r/'Nintendo-3DS-IA/consola/Nintendo3DSIA.cia','/cias/Nintendo3DSIA.cia'),(r/'Nintendo-3DS-IA/consola/Nintendo3DSIA.3dsx','/3ds/Nintendo3DSIA/Nintendo3DSIA.3dsx'),(r/'Tamagotchi-3DS/TamaConnectionV2.cia','/cias/TamaConnectionV2.cia'),(r/'Tamagotchi-3DS/TamaConnectionV2.3dsx','/3ds/TamaConnectionV2/TamaConnectionV2.3dsx')])
log=[]
with ftplib.FTP() as f:
 f.connect('192.168.1.123',5000,timeout=25);f.login();f.set_pasv(True)
 try:print('Espacio:',f.sendcmd('STAT /'),flush=True)
 except ftplib.all_errors:pass
 for local,remote in sorted(files,key=lambda x:x[0].stat().st_size):
  parent=remote.rsplit('/',1)[0];walk=''
  for part in parent.strip('/').split('/'):
   if not part:continue
   walk+='/'+part
   try:f.mkd(walk)
   except (ftplib.error_perm,ftplib.error_temp) as e:
    if not str(e).startswith(('450','550','521')):raise
  raw=local.read_bytes();old=io.BytesIO()
  try:f.retrbinary('RETR '+remote,old.write)
  except (ftplib.error_perm,ftplib.error_temp) as e:
   if not str(e).startswith(('450','550')):raise
  if old.getvalue()==raw:print('Ya actualizado:',remote,flush=True);log.append({'path':remote,'status':'unchanged'});continue
  temp=remote+'.upload';sent=0;mark=time.monotonic();print('Transfiriendo',remote,len(raw),'bytes',flush=True)
  def progress(block):
   global sent,mark
   sent+=len(block);now=time.monotonic()
   if now-mark>20:print(remote,round(100*sent/len(raw),1),'%',flush=True);mark=now
  f.storbinary('STOR '+temp,io.BytesIO(raw),blocksize=32768,callback=progress)
  h=hashlib.sha256();f.retrbinary('RETR '+temp,h.update,blocksize=32768);assert h.digest()==hashlib.sha256(raw).digest()
  if old.getvalue():f.rename(remote,remote+'.backup-'+uuid.uuid4().hex[:6])
  f.rename(temp,remote);print('Verificado:',remote,flush=True);log.append({'path':remote,'status':'transferred','sha256':h.hexdigest(),'bytes':len(raw)})
(r/'Linux-2DS-XL/transferencia.json').write_text(json.dumps(log,indent=2));print('TRANSFERENCIA_COMPLETA',flush=True)
