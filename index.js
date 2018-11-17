// require the discord.js module
const { Client, RichEmbed } = require('discord.js');
const { prefix, announceid, generalid, profilesid, token } = require('./config.json');
// create a new Discord client
const client = new Client();
// when the client is ready, run this code
// this event will trigger whenever your bot:
// - finishes logging in
// - reconnects after disconnecting
client.on('ready', () => {
    console.log('Ready!');
    client.user.setActivity('!ping', { type: 'PLAYING' });
});
client.on('guildCreate', () => {
    const general = client.channels.get(generalid);
    // This event triggers when the bot joins a guild.
    general.send('Hello there! My name is TOM, short for Target Operations Machine, and I am designed to manage target randomization and distribution.');
    client.user.setActivity(`Serving ${client.guilds.size} servers`);
});
client.on('guildMemberAdd', member => {
    const general = client.channels.get(generalid);
    const profiles = client.channels.get(profilesid);
    general.send(`Welcome to the server, ${member}. If you would like to participate in future games, please submit your name, grade, and a picture of yourself to ${profiles}.`);
});
client.on('message', async message => {
    if(!message.content.startsWith(prefix) || !message.member.roles.some(role =>['admin'].includes(role.name)) || message.author.bot) return;
    const args = message.content.slice(prefix.length).trim().split(/ +/g);
    const command = args.shift().toLowerCase();

    if(command === 'nick') {
        const nickmember = message.mentions.members.first() || message.guild.members.get(args[0]);
        if(!nickmember) {
            return message.reply('Please mention a valid member of this server');
        }
        let nick = args.slice(1).join(' ');
        if(!nick) nick = '';

        // Nick
        await nickmember.setNickname(nick)
          .catch(error => message.channel.send(`Sorry ${message.author} I couldn't do that because of : ${error}`));
        message.channel.send(`${nickmember.user}'s nickname has been changed by ${message.author} to: ${nick}`);
    }
    if(command === 'ping') {
        message.channel.send('pong!');
    }
    if (command === 'announce') {
        const announcements = client.channels.get(announceid);
        if (!message.member.roles.some(role =>['game mod'].includes(role.name))) {
            return message.reply('you do not have permissions to use this command');
        }
        if (!args[0]) {
            return message.reply('please specify what to announce. Valid arguments are:\n``!announce deaths``\n``!announce signups``');
        }
        if (args[0] === 'signups') {
            announcements.send('@everyone, we will be starting a new round of "Last Man Standing" soon. Please react to this post with 👍 to sign up. Signups will close in about two days.').then(sentMessage => {
                sentMessage.react('👍');
                client.on('messageReactionAdd', (reaction, user) => {
                    if(reaction.emoji.name === '👍') {
                        console.log(reaction.users);
                    }
                });
            });
        }
        if (args[0] === 'deaths') {
        const assassin = message.guild.roles.find('name', 'assassin');
        // First Embed Settings
        const embed = new RichEmbed()
          .setTitle('Today\'s deaths:')
          .setColor(0x0000FF)
          .setDescription('dead person\nanother dead person\nreafy player two');
        // Second Embed Settings
        const embed2 = new RichEmbed()
          .setTitle('Remaining Assassins:')
          .setColor(0xFF0000)
          .setDescription('not dead yet\nstayin\' alive\nstill alive person');
        // Send the embed to announcements
        announcements.send(`${assassin}`);
        announcements.send(embed);
        announcements.send(embed2);
        }
    }
});
// login to Discord with your app's token
client.login(token);