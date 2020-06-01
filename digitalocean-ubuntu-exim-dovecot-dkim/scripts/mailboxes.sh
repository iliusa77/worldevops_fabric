#!/bin/sh

echo "1 - list of mailboxes"
echo "2 - add new mailbox"
echo "3 - delete exists mailbox"
echo "4 - add alias"
echo "Please enter number of action:"

read action

case $action in
     1)
          echo "This domain has next mailboxes:"
          ls -1 /home/vmail/demo.loc
          ;;
     2)
          echo "Enter username password"
          read mailuser pass
          if [ -d /home/vmail/demo.loc/$mailuser ]; then
            echo "This user already exists, please enter another name";
            exit;
          else
            hash=`doveadm pw -s MD5 -p $pass | sed 's/{MD5}//'`
            user=`echo $mailuser |cut -d'@' -f1`
            domain=`echo $mailuser |cut -d'@' -f2`
            mkdir -p /home/vmail/demo.loc/$user
            chown -R vmail:vmail /home/vmail/demo.loc/$user
            echo "$mailuser@demo.loc:$hash:120:120::/home/vmail/demo.loc/$user:" >> /etc/dovecot/passwd
          fi
          echo "Mailbox added"
          ;;
     3)
          echo "Enter username"
          read mailuser
          sed /$mailuser/d /etc/dovecot/passwd
          echo "Mailbox deleted from mailserver"
          echo "Please, remove directory of user from /home/vmail/demo.loc manually"
          ;; 
     4)
          echo "Enter aliasname mailbox"
          read alias mailbox
          echo "$alias@demo.loc: $mailbox@demo.loc" >> /etc/exim4/aliases
          echo "Alias added"
          ;;
     *)   echo "Unknown action"
          ;;
esac
exit