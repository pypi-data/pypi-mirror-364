def parse_messages(service, messages, next_page_token):
    if not messages:
        print("No messages remain.")
        return None
    
    else:
        for message in messages:
            message_id = message["id"] 
            msg = (
                service.users()
                .messages()
                .get(userId="me", id=message["id"], format="raw")
                .execute()
            )
            msg_str = base64.urlsafe_b64decode(msg["raw"].encode("ASCII"))
            raw_email_path = raw_dir / f'email_{message["id"]}.eml'
            print(f'\nRetrieving message {raw_email_path.name}.')
            with open(raw_email_path, "wb") as f:
                f.write(msg_str)
            attachments = clean_email(raw_email_path, config, message_id)
            if attachments:
                total_attachments += attachments

        total_messages += len(messages)
        return

    if not next_page_token:
        return None
    

    while True:
        messages, next_page_token = get_messages_and_next_page(service, query)

        if not messages:
            print("No messages remain.")
            break
        else:
            for message in messages:
                message_id = message["id"] 
                msg = (
                    service.users()
                    .messages()
                    .get(userId="me", id=message["id"], format="raw")
                    .execute()
                )
                msg_str = base64.urlsafe_b64decode(msg["raw"].encode("ASCII"))
                raw_email_path = raw_dir / f'email_{message["id"]}.eml'
                print(f'\nRetrieving message {raw_email_path.name}.')
                with open(raw_email_path, "wb") as f:
                    f.write(msg_str)
                attachments = clean_email(raw_email_path, config, message_id)
                if attachments:
                    total_attachments += attachments

            total_messages += len(messages)

        if not next_page_token:
            break

    print("\nDone.")
    print(f"Retrieved {total_messages} messages and {total_attachments} attachments.")
    return {"total_messages": total_messages, "total_attachments": total_attachments}