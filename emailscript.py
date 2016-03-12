import csv
import smtplib
import argparse
import os
import sys
import base64

# arguments & documentation
p = argparse.ArgumentParser(description="Email all .py scripts in a folder to the @umich emails specified by the filenames. NOTE: Be sure to set your gmail up by enabling access for 'less secure apps': https://www.google.com/settings/security/lesssecureapps")
p.add_argument("--sendfrom", help="The email address to send from (i.e. your gmail)")
p.add_argument("--password", help="Password for the 'send from' address.")
p.add_argument("--subject", help = "A subject line for the email.",default="PH 141 python code")
p.add_argument("--body", help = "A message for the body of the email. You may use (e.g.) \\n for a newline.", default="Hi!\n\nThe python code which you recently turned in is attached for your reference.")
p.add_argument("--directory", help="The directory containing all the .py files")
args=p.parse_args()

# check to see if some argument wasn't specified correctly
for k in vars(args).keys():
	if vars(args)[k]==None:
		print("You have failed to specify a \"{}\" value!".format(k))
		sys.exit()

def main():

	# log in to gmail
	server = smtplib.SMTP('smtp.gmail.com:587')
	server.starttls()
	server.login(args.sendfrom,args.password)

	# allow users to specify directory w / or without
	if args.directory[-1]!="/":
		args.directory+="/"
	# get list of files in directory
	fnames=os.listdir(args.directory)
	# choose only python files
	pyfiles=[s for s in fnames if s[-3:]==".py"]
	# make list of email addresses
	emails=[s[:-3]+"@umich.edu" for s in pyfiles]
	# and file paths
	pyfilepaths=[args.directory+s for s in fnames]
	nf=len(pyfiles)
	# this is just an arbitrary string to use as a divider
	marker="AUNIQUEMARKER" 

	# loop through files
	for i in range(nf):
		f=open(pyfilepaths[i],'rt')
		# encode the .py file and any escaped characters in the body
		# it's a little different between python versions
		if sys.version_info < (3, 0):
			encoded=base64.b64encode(f.read())
			body=args.body.decode('unicode_escape')
		else:
			encoded=base64.b64encode(bytes(f.read(), 'UTF-8'))
			body=bytes(args.body,'UTF-8').decode('unicode_escape')
		# main headers
		headers = """From: <{}>\nTo: <{}>\nSubject: {}\nMIME-Version: 1.0\nContent-Type: multipart/mixed; boundary={}\n--{}\n""".format(args.sendfrom,emails[i],args.subject,marker,marker)
		# message action
		msgact = """Content-Type: text/plain\nContent-Transfer-Encoding:8bit\n{}\n--{}\n""".format(body,marker)
		# attachment section
		attachment = """Content-Type: multipart/mixed; name=\"{}\"\nContent-Transfer-Encoding:base64\nContent-Disposition: attachment; filename={}\n{}\n--{}--\n""".format(pyfiles[i], pyfiles[i], encoded, marker)
		# send email
		try:
			server.sendmail(args.sendfrom, emails[i], headers+msgact+attachment)
			print("Sent email to {}".format(emails[i]))
		except Exception:
			print("ERROR: could not send email to {}".format(emails[i]))
	server.quit()
main()
